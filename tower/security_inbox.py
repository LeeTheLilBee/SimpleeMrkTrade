# =============================================================================
# THE TOWER — SECURITY INBOX
# FILE: tower/security_inbox.py
# =============================================================================

import hashlib
import json
import inspect
import os
import secrets
from datetime import datetime, timezone
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



# =============================================================================
# PACK 016 — SECURITY INBOX GROUPING + CLEANUP
# =============================================================================

def _group_key_for_item(item: Dict[str, Any]) -> str:
    """
    Creates a stable group key.

    Baby version:
    Instead of treating every repeated scream as brand new,
    we put similar screams in the same basket.
    """

    source_type = item.get("source_type") or "unknown"
    reason_code = item.get("reason_code") or "unknown"
    app_name = item.get("app_name") or "unknown"
    user_id = item.get("user_id") or "unknown"

    # Some repeated noisy events should group by reason/app/user.
    if source_type == "security_event":
        return f"security_event:{app_name}:{user_id}:{reason_code}"

    # Evidence capsules are usually grouped by reason + app.
    if source_type == "evidence_capsule":
        return f"evidence_capsule:{app_name}:{reason_code}"

    # Exports grouped by app + user + reason.
    if source_type == "export":
        return f"export:{app_name}:{user_id}:{reason_code}"

    # Admin actions grouped by action/reason/target app.
    if source_type == "admin_action":
        source_payload = item.get("source_payload") or {}
        admin_action = source_payload.get("admin_action") or item.get("title") or "admin_action"
        return f"admin_action:{app_name}:{admin_action}:{reason_code}"

    # Step-ups grouped by app + user + reason.
    if source_type == "step_up_challenge":
        return f"step_up:{app_name}:{user_id}:{reason_code}"

    return f"{source_type}:{app_name}:{user_id}:{reason_code}"


def _priority_for_group(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates group priority.

    Baby version:
    The loudest/scariest child in the group decides the group danger level.
    """

    if not items:
        return {
            "priority": "low",
            "priority_score": 0,
            "highest_severity": "info",
            "highest_severity_rank": 0,
        }

    highest_rank = max(int(item.get("severity_rank") or 0) for item in items)

    highest_severity = "info"
    for name, rank in SEVERITY_ORDER.items():
        if rank == highest_rank:
            highest_severity = name
            break

    open_count = len([item for item in items if item.get("status") == INBOX_STATUS_OPEN])
    reviewing_count = len([item for item in items if item.get("status") == INBOX_STATUS_REVIEWING])

    priority_score = highest_rank * 100 + open_count * 5 + reviewing_count * 2

    if highest_rank >= 4:
        priority = "urgent"
    elif highest_rank == 3:
        priority = "high"
    elif highest_rank == 2:
        priority = "medium"
    else:
        priority = "low"

    return {
        "priority": priority,
        "priority_score": priority_score,
        "highest_severity": highest_severity,
        "highest_severity_rank": highest_rank,
    }


def build_security_review_queue(
    include_resolved: bool = False,
    limit_groups: int = 25,
) -> List[Dict[str, Any]]:
    """
    Builds a grouped review queue.

    Baby version:
    This turns many individual alerts into a smaller stack of review cards.
    """

    data = _load_raw()
    rows = data.get("items", [])

    if not include_resolved:
        rows = [
            item for item in rows
            if item.get("status") not in {INBOX_STATUS_RESOLVED, INBOX_STATUS_DISMISSED}
        ]

    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for item in rows:
        key = _group_key_for_item(item)
        grouped.setdefault(key, []).append(item)

    queue: List[Dict[str, Any]] = []

    for group_key, items in grouped.items():
        priority = _priority_for_group(items)

        sorted_items = sorted(
            items,
            key=lambda item: (
                -int(item.get("severity_rank") or 0),
                item.get("created_at") or "",
            ),
        )

        representative = sorted_items[0]

        open_count = len([item for item in items if item.get("status") == INBOX_STATUS_OPEN])
        reviewing_count = len([item for item in items if item.get("status") == INBOX_STATUS_REVIEWING])
        resolved_count = len([item for item in items if item.get("status") == INBOX_STATUS_RESOLVED])
        dismissed_count = len([item for item in items if item.get("status") == INBOX_STATUS_DISMISSED])

        queue.append({
            "group_key": group_key,
            "title": representative.get("title"),
            "summary": representative.get("summary"),
            "recommended_action": representative.get("recommended_action"),
            "source_type": representative.get("source_type"),
            "app_name": representative.get("app_name"),
            "user_id": representative.get("user_id"),
            "reason_code": representative.get("reason_code"),
            "priority": priority.get("priority"),
            "priority_score": priority.get("priority_score"),
            "highest_severity": priority.get("highest_severity"),
            "highest_severity_rank": priority.get("highest_severity_rank"),
            "total_items": len(items),
            "open_count": open_count,
            "reviewing_count": reviewing_count,
            "resolved_count": resolved_count,
            "dismissed_count": dismissed_count,
            "first_seen_at": min(item.get("created_at") or "" for item in items),
            "last_seen_at": max(item.get("created_at") or "" for item in items),
            "sample_item_ids": [
                item.get("inbox_item_id")
                for item in sorted_items[:5]
            ],
            "items": sorted_items[:10],
        })

    queue.sort(
        key=lambda group: (
            -int(group.get("priority_score") or 0),
            group.get("first_seen_at") or "",
        )
    )

    return queue[:limit_groups]


def get_security_review_queue_summary() -> Dict[str, Any]:
    queue = build_security_review_queue(include_resolved=False, limit_groups=1000)

    summary = {
        "total_review_groups": len(queue),
        "urgent": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "total_open_items_in_groups": 0,
        "largest_group_size": 0,
        "by_source_type": {},
        "by_app": {},
    }

    for group in queue:
        priority = group.get("priority") or "low"
        source_type = group.get("source_type") or "unknown"
        app_name = group.get("app_name") or "unknown"

        if priority in summary:
            summary[priority] += 1

        summary["total_open_items_in_groups"] += int(group.get("open_count") or 0)
        summary["largest_group_size"] = max(
            summary["largest_group_size"],
            int(group.get("total_items") or 0),
        )

        summary["by_source_type"][source_type] = summary["by_source_type"].get(source_type, 0) + 1
        summary["by_app"][app_name] = summary["by_app"].get(app_name, 0) + 1

    return summary


def bulk_update_inbox_items(
    inbox_item_ids: List[str],
    status: str,
    actor_user_id: str,
    resolution_note: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Bulk updates specific inbox items.

    Baby version:
    Owner can clean a pile at once instead of clicking each item.
    """

    updated = []
    missing = []

    for inbox_item_id in inbox_item_ids:
        item = update_inbox_item_status(
            inbox_item_id=inbox_item_id,
            status=status,
            actor_user_id=actor_user_id,
            resolution_note=resolution_note,
        )

        if item:
            updated.append(inbox_item_id)
        else:
            missing.append(inbox_item_id)

    return {
        "status": "complete",
        "requested": len(inbox_item_ids),
        "updated": len(updated),
        "missing": len(missing),
        "updated_item_ids": updated,
        "missing_item_ids": missing,
    }


def bulk_update_group(
    group_key: str,
    status: str,
    actor_user_id: str,
    resolution_note: Optional[str] = None,
    max_items: int = 100,
) -> Dict[str, Any]:
    """
    Bulk updates a grouped review queue.

    Baby version:
    If a group is test noise, owner can resolve/dismiss the group together.
    """

    data = _load_raw()
    matching = [
        item for item in data.get("items", [])
        if _group_key_for_item(item) == group_key
        and item.get("status") not in {INBOX_STATUS_RESOLVED, INBOX_STATUS_DISMISSED}
    ][:max_items]

    return bulk_update_inbox_items(
        inbox_item_ids=[item.get("inbox_item_id") for item in matching],
        status=status,
        actor_user_id=actor_user_id,
        resolution_note=resolution_note,
    )


def archive_test_noise(
    actor_user_id: str = "owner_solice",
    max_items: int = 500,
) -> Dict[str, Any]:
    """
    Dismisses obvious Pack/test noise from the inbox.

    Baby version:
    This is the broom. It sweeps old test clutter out of the active review desk.
    """

    data = _load_raw()
    candidates = []

    test_markers = [
        "pack_",
        "test",
        "manual_test",
        "Pack 0",
        "PACK_",
    ]

    for item in data.get("items", []):
        if item.get("status") in {INBOX_STATUS_RESOLVED, INBOX_STATUS_DISMISSED}:
            continue

        blob = _safe_json({
            "title": item.get("title"),
            "summary": item.get("summary"),
            "reason_code": item.get("reason_code"),
            "source_payload": item.get("source_payload"),
        })

        if any(marker in blob for marker in test_markers):
            candidates.append(item)

    candidates = candidates[:max_items]

    result = bulk_update_inbox_items(
        inbox_item_ids=[item.get("inbox_item_id") for item in candidates],
        status=INBOX_STATUS_DISMISSED,
        actor_user_id=actor_user_id,
        resolution_note="Archived by Pack 016 test-noise cleanup.",
    )

    return {
        **result,
        "cleanup_type": "archive_test_noise",
    }


def rebuild_security_inbox_dedupe() -> Dict[str, Any]:
    """
    Removes exact duplicate dedupe keys, keeping the newest active item.

    Baby version:
    If the same alert got copied twice, keep one copy.
    """

    data = _load_raw()
    rows = data.get("items", [])

    seen = {}
    kept = []
    removed = []

    # Newest first, so we keep newest.
    rows_sorted = sorted(rows, key=lambda item: item.get("created_at") or "", reverse=True)

    for item in rows_sorted:
        key = item.get("dedupe_key")
        if not key:
            kept.append(item)
            continue

        if key in seen:
            removed.append(item)
            continue

        seen[key] = True
        kept.append(item)

    # Restore chronological-ish order.
    kept = sorted(kept, key=lambda item: item.get("created_at") or "")

    data["items"] = kept
    _save_raw(data)

    write_audit_event(
        actor_user_id="tower_security_inbox",
        target_user_id=None,
        action="rebuild_security_inbox_dedupe",
        app_name="tower_admin",
        object_type="security_inbox",
        object_id="security_inbox",
        result="allow",
        reason_code="security_inbox_dedupe_rebuilt",
        human_reason="Tower security inbox dedupe was rebuilt.",
        risk_score=20,
        risk_state="clear",
        metadata={
            "kept": len(kept),
            "removed": len(removed),
        },
    )

    return {
        "status": "complete",
        "kept": len(kept),
        "removed": len(removed),
    }



# =============================================================================
# PACK 017 — SECURITY INBOX REVIEW ACTIONS
# =============================================================================
# Baby version:
# These are backend “buttons” for the Security Inbox.
# The dashboard can later call these to resolve, dismiss, reopen, escalate,
# quarantine, require step-up, and add notes.

INBOX_ACTION_RESOLVE = "resolve"
INBOX_ACTION_DISMISS = "dismiss"
INBOX_ACTION_REOPEN = "reopen"
INBOX_ACTION_ESCALATE = "escalate"
INBOX_ACTION_QUARANTINE_USER = "quarantine_user"
INBOX_ACTION_REQUIRE_STEP_UP = "require_step_up"
INBOX_ACTION_ADD_NOTE = "add_note"

INBOX_STATUS_ESCALATED = "escalated"






def _pack017_create_evidence_capsule_safe(**kwargs):
    """
    Signature-safe wrapper for evidence capsule creation.

    Security Inbox escalation should never fail just because the evidence
    capsule function expects stricter argument shapes. This wrapper:
    - filters unsupported kwargs
    - supplies missing user/app_name
    - converts user_id strings into user-like dictionaries when needed
    - preserves overflow context safely
    """
    try:
        import inspect
        from tower.evidence_capsules import create_evidence_capsule as _real_create_evidence_capsule

        sig = inspect.signature(_real_create_evidence_capsule)
        allowed = set(sig.parameters.keys())

        actor_user_id = (
            kwargs.get("actor_user_id")
            or kwargs.get("reviewed_by")
            or kwargs.get("owner_user_id")
            or kwargs.get("user_id")
            or "system"
        )

        related_user_id = (
            kwargs.get("user_id")
            or kwargs.get("target_user_id")
            or kwargs.get("actor_user_id")
            or actor_user_id
            or "system"
        )

        app_name_value = (
            kwargs.get("app_name")
            or kwargs.get("source_app")
            or kwargs.get("target_app")
            or kwargs.get("app")
            or "tower_admin"
        )

        # Load a real Tower user record when available.
        user_obj = None
        try:
            from tower.user_store import get_user
            user_obj = get_user(actor_user_id)
        except Exception:
            user_obj = None

        if not isinstance(user_obj, dict):
            user_obj = {
                "user_id": actor_user_id,
                "id": actor_user_id,
                "role": "owner" if str(actor_user_id).startswith("owner") else "user",
                "account_type": "owner" if str(actor_user_id).startswith("owner") else "beta_user",
                "status": "active",
            }

        # Required compatibility for evidence_capsules.create_evidence_capsule.
        if "user" in allowed:
            current_user_arg = kwargs.get("user")
            if isinstance(current_user_arg, dict):
                kwargs["user"] = current_user_arg
            else:
                kwargs["user"] = user_obj

        if "user_id" in allowed and "user_id" not in kwargs:
            kwargs["user_id"] = related_user_id

        if "app_name" in allowed:
            kwargs["app_name"] = app_name_value

        # Helpful aliases for different capsule signatures.
        if "source_app" in allowed and "source_app" not in kwargs:
            kwargs["source_app"] = app_name_value

        if "actor_user_id" in allowed and "actor_user_id" not in kwargs:
            kwargs["actor_user_id"] = actor_user_id

        if "related_user_id" in allowed and "related_user_id" not in kwargs:
            kwargs["related_user_id"] = related_user_id

        filtered = {k: v for k, v in kwargs.items() if k in allowed}
        overflow = {k: v for k, v in kwargs.items() if k not in allowed}

        if overflow:
            if "context" in allowed:
                context = filtered.get("context")
                if not isinstance(context, dict):
                    context = {}
                context.setdefault("security_inbox_overflow", overflow)
                filtered["context"] = context

            elif "metadata" in allowed:
                metadata = filtered.get("metadata")
                if not isinstance(metadata, dict):
                    metadata = {}
                metadata.setdefault("security_inbox_overflow", overflow)
                filtered["metadata"] = metadata

        result = _real_create_evidence_capsule(**filtered)

        if isinstance(result, dict):
            return result

        return {
            "capsule_result": result,
            "human_reason": "Evidence capsule creation returned a non-dict result.",
        }

    except Exception as exc:
        return {
            "error": str(exc),
            "human_reason": "Evidence capsule creation failed, but inbox item was still escalated.",
        }


def _pack017_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _pack017_find_item(inbox_item_id: str) -> Optional[Dict[str, Any]]:
    data = _load_raw()
    for item in data.get("items", []):
        if item.get("inbox_item_id") == inbox_item_id:
            return item
    return None


def _pack017_save_item(updated_item: Dict[str, Any]) -> Dict[str, Any]:
    data = _load_raw()
    rows = data.get("items", [])

    saved = False
    for idx, item in enumerate(rows):
        if item.get("inbox_item_id") == updated_item.get("inbox_item_id"):
            rows[idx] = updated_item
            saved = True
            break

    if not saved:
        rows.append(updated_item)

    data["items"] = rows
    _save_raw(data)
    return updated_item


def _pack017_add_note_to_item(
    item: Dict[str, Any],
    actor_user_id: str,
    note: str,
    action: str,
) -> Dict[str, Any]:
    notes = item.get("review_notes")
    if not isinstance(notes, list):
        notes = []

    notes.append({
        "actor_user_id": actor_user_id,
        "action": action,
        "note": note,
        "created_at": _pack017_now(),
    })

    item["review_notes"] = notes
    item["last_reviewed_by"] = actor_user_id
    item["last_reviewed_at"] = _pack017_now()
    return item


def _pack017_audit_review_action(
    actor_user_id: str,
    action: str,
    item: Optional[Dict[str, Any]],
    result: str,
    reason_code: str,
    human_reason: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    try:
        write_audit_event(
            actor_user_id=actor_user_id,
            target_user_id=(item or {}).get("user_id"),
            action=f"security_inbox_{action}",
            app_name="tower_admin",
            object_type="security_inbox_item",
            object_id=(item or {}).get("inbox_item_id"),
            result=result,
            reason_code=reason_code,
            human_reason=human_reason,
            risk_score=int((item or {}).get("severity_rank") or 0) * 20,
            risk_state="clear" if result == "allow" else "restricted",
            metadata=metadata or {},
        )
    except Exception:
        # Never let audit failure crash the review action in notebook testing.
        pass


def perform_inbox_item_action(
    inbox_item_id: str,
    action: str,
    actor_user_id: str = "owner_solice",
    note: str = "",
    resolution_note: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Performs one review action on one inbox item.

    Baby version:
    This is one button press for one alert.
    """

    item = _pack017_find_item(inbox_item_id)

    if not item:
        return {
            "ok": False,
            "reason_code": "inbox_item_not_found",
            "human_reason": "Security inbox item was not found.",
            "inbox_item_id": inbox_item_id,
            "action": action,
        }

    before_status = item.get("status")
    now = _pack017_now()

    if action == INBOX_ACTION_RESOLVE:
        item["status"] = INBOX_STATUS_RESOLVED
        item["resolved_at"] = now
        item["resolved_by"] = actor_user_id
        item["resolution_note"] = resolution_note or note or "Resolved from Security Inbox review action."
        item = _pack017_add_note_to_item(item, actor_user_id, item["resolution_note"], action)

    elif action == INBOX_ACTION_DISMISS:
        item["status"] = INBOX_STATUS_DISMISSED
        item["dismissed_at"] = now
        item["dismissed_by"] = actor_user_id
        item["dismissal_note"] = resolution_note or note or "Dismissed from Security Inbox review action."
        item = _pack017_add_note_to_item(item, actor_user_id, item["dismissal_note"], action)

    elif action == INBOX_ACTION_REOPEN:
        item["status"] = INBOX_STATUS_OPEN
        item["reopened_at"] = now
        item["reopened_by"] = actor_user_id
        item["reopen_note"] = resolution_note or note or "Reopened from Security Inbox review action."
        item = _pack017_add_note_to_item(item, actor_user_id, item["reopen_note"], action)

    elif action == INBOX_ACTION_ADD_NOTE:
        item = _pack017_add_note_to_item(
            item,
            actor_user_id,
            note or "Reviewed from Security Inbox.",
            action,
        )

    elif action == INBOX_ACTION_ESCALATE:
        item["status"] = INBOX_STATUS_ESCALATED
        item["escalated_at"] = now
        item["escalated_by"] = actor_user_id
        item["escalation_note"] = note or "Escalated from Security Inbox."

        # Try to create an evidence capsule for the escalation.
        capsule = None
        try:
            from tower.evidence_capsules import create_evidence_capsule

            capsule = _pack017_create_evidence_capsule_safe(
                trigger="security_inbox_escalation",
                user_id=item.get("user_id"),
                request={
                    "action": "security_inbox_escalation",
                    "app_name": item.get("app_name") or "tower_admin",
                    "object_type": "security_inbox_item",
                    "object_id": item.get("inbox_item_id"),
                },
                decision={
                    "allowed": False,
                    "decision": "escalate",
                    "reason_code": "security_inbox_item_escalated",
                    "human_reason": item.get("summary") or "Security inbox item was escalated.",
                    "risk_score": int(item.get("severity_rank") or 0) * 20,
                    "risk_state": item.get("severity") or "high",
                    "required_actions": ["owner_review_required"],
                    "metadata": {
                        "inbox_item_id": item.get("inbox_item_id"),
                        "source_type": item.get("source_type"),
                        "reason_code": item.get("reason_code"),
                    },
                },
                policy_report=None,
                context={
                    "inbox_item": item,
                },
                notes=note or "Security Inbox escalation capsule.",
                created_by=actor_user_id,
            )
        except Exception as exc:
            capsule = {
                "error": str(exc),
                "human_reason": "Evidence capsule creation failed, but inbox item was still escalated.",
            }

        item["escalation_capsule"] = capsule
        item = _pack017_add_note_to_item(item, actor_user_id, item["escalation_note"], action)

    elif action == INBOX_ACTION_QUARANTINE_USER:
        item["status"] = INBOX_STATUS_ESCALATED
        item["quarantine_requested_at"] = now
        item["quarantine_requested_by"] = actor_user_id
        item["quarantine_note"] = note or "User quarantine requested from Security Inbox."

        # In this pack, we record the quarantine request.
        # Later packs can wire this to a hard user/session mutation.
        item["requested_tower_actions"] = item.get("requested_tower_actions") or []
        item["requested_tower_actions"].append({
            "action": "quarantine_user",
            "user_id": item.get("user_id"),
            "requested_by": actor_user_id,
            "requested_at": now,
            "note": item["quarantine_note"],
        })

        item = _pack017_add_note_to_item(item, actor_user_id, item["quarantine_note"], action)

    elif action == INBOX_ACTION_REQUIRE_STEP_UP:
        item["status"] = INBOX_STATUS_ESCALATED
        item["step_up_requested_at"] = now
        item["step_up_requested_by"] = actor_user_id
        item["step_up_note"] = note or "Step-up requested from Security Inbox."

        challenge = None
        try:
            from tower.step_up import create_step_up_challenge

            challenge = create_step_up_challenge(
                user_id=item.get("user_id") or actor_user_id,
                app_name=item.get("app_name") or "tower_admin",
                action="security_inbox_review",
                reason_code="security_inbox_step_up_required",
                object_type="security_inbox_item",
                object_id=item.get("inbox_item_id"),
            )
        except Exception as exc:
            challenge = {
                "error": str(exc),
                "human_reason": "Step-up challenge creation failed, but request was recorded.",
            }

        item["step_up_challenge"] = challenge
        item = _pack017_add_note_to_item(item, actor_user_id, item["step_up_note"], action)

    else:
        return {
            "ok": False,
            "reason_code": "unsupported_inbox_action",
            "human_reason": f"Unsupported Security Inbox action: {action}",
            "inbox_item_id": inbox_item_id,
            "action": action,
            "status_before": before_status,
        }

    item["updated_at"] = now
    item["last_action"] = action

    saved = _pack017_save_item(item)

    _pack017_audit_review_action(
        actor_user_id=actor_user_id,
        action=action,
        item=item,
        result="allow",
        reason_code=f"security_inbox_{action}_complete",
        human_reason=f"Security Inbox item action complete: {action}",
        metadata={
            "status_before": before_status,
            "status_after": item.get("status"),
            "note": note or resolution_note,
        },
    )

    return {
        "ok": True,
        "reason_code": f"security_inbox_{action}_complete",
        "human_reason": f"Security Inbox item action complete: {action}",
        "inbox_item_id": inbox_item_id,
        "action": action,
        "status_before": before_status,
        "status_after": saved.get("status"),
        "item": saved,
    }


def perform_inbox_group_action(
    group_key: str,
    action: str,
    actor_user_id: str = "owner_solice",
    note: str = "",
    max_items: int = 100,
) -> Dict[str, Any]:
    """
    Performs one review action on every open/reviewing/escalated item in a group.

    Baby version:
    This is one button press for a whole pile of similar alerts.
    """

    data = _load_raw()

    candidates = [
        item for item in data.get("items", [])
        if _group_key_for_item(item) == group_key
        and item.get("status") not in {INBOX_STATUS_RESOLVED, INBOX_STATUS_DISMISSED}
    ][:max_items]

    results = []
    for item in candidates:
        results.append(
            perform_inbox_item_action(
                inbox_item_id=item.get("inbox_item_id"),
                action=action,
                actor_user_id=actor_user_id,
                note=note,
                resolution_note=note,
            )
        )

    ok_count = len([result for result in results if result.get("ok")])
    failed_count = len(results) - ok_count

    _pack017_audit_review_action(
        actor_user_id=actor_user_id,
        action=f"group_{action}",
        item=None,
        result="allow",
        reason_code=f"security_inbox_group_{action}_complete",
        human_reason=f"Security Inbox group action complete: {action}",
        metadata={
            "group_key": group_key,
            "requested": len(candidates),
            "ok_count": ok_count,
            "failed_count": failed_count,
        },
    )

    return {
        "ok": failed_count == 0,
        "reason_code": f"security_inbox_group_{action}_complete",
        "human_reason": f"Security Inbox group action complete: {action}",
        "group_key": group_key,
        "action": action,
        "requested": len(candidates),
        "ok_count": ok_count,
        "failed_count": failed_count,
        "results": results[:10],
    }


def list_available_inbox_actions() -> List[Dict[str, Any]]:
    """
    Lists backend review actions.

    Baby version:
    These are the future dashboard buttons.
    """

    return [
        {
            "action": INBOX_ACTION_RESOLVE,
            "label": "Resolve",
            "human_reason": "Mark the alert as handled.",
            "danger_level": "low",
        },
        {
            "action": INBOX_ACTION_DISMISS,
            "label": "Dismiss",
            "human_reason": "Hide low-value or test-noise alerts from the active queue.",
            "danger_level": "low",
        },
        {
            "action": INBOX_ACTION_REOPEN,
            "label": "Reopen",
            "human_reason": "Put a resolved/dismissed alert back into active review.",
            "danger_level": "medium",
        },
        {
            "action": INBOX_ACTION_ADD_NOTE,
            "label": "Add note",
            "human_reason": "Attach an owner/admin note to an alert.",
            "danger_level": "low",
        },
        {
            "action": INBOX_ACTION_ESCALATE,
            "label": "Escalate",
            "human_reason": "Escalate an alert and try to create an evidence capsule.",
            "danger_level": "high",
        },
        {
            "action": INBOX_ACTION_REQUIRE_STEP_UP,
            "label": "Require step-up",
            "human_reason": "Request extra authorization before continuing.",
            "danger_level": "high",
        },
        {
            "action": INBOX_ACTION_QUARANTINE_USER,
            "label": "Quarantine user",
            "human_reason": "Record a quarantine request for the related user.",
            "danger_level": "critical",
        },
    ]


def get_security_inbox_action_summary() -> Dict[str, Any]:
    """
    Summarizes review actions already applied.
    """

    data = _load_raw()

    summary = {
        "total_items": 0,
        "with_review_notes": 0,
        "escalated": 0,
        "quarantine_requested": 0,
        "step_up_requested": 0,
        "by_last_action": {},
    }

    for item in data.get("items", []):
        summary["total_items"] += 1

        if item.get("review_notes"):
            summary["with_review_notes"] += 1

        if item.get("status") == INBOX_STATUS_ESCALATED:
            summary["escalated"] += 1

        if item.get("quarantine_requested_at"):
            summary["quarantine_requested"] += 1

        if item.get("step_up_requested_at"):
            summary["step_up_requested"] += 1

        last_action = item.get("last_action") or "none"
        summary["by_last_action"][last_action] = summary["by_last_action"].get(last_action, 0) + 1

    return summary

