
from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"
ARCHIVE_HANDOFF_PATH = DATA_DIR / "archive_vault_handoff_queue.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _load_json_list(path: Path) -> List[Dict[str, Any]]:
    try:
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return [item for item in data.get("items", []) if isinstance(item, dict)]
        return []
    except Exception:
        return []


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)


def _redact_for_archive(value: Any) -> Any:
    tokenish = ["token", "keycard", "secret", "password", "authorization", "auth_header", "bearer"]

    if isinstance(value, dict):
        clean = {}
        removed = 0
        for key, item in value.items():
            key_text = str(key).lower()
            if any(marker in key_text for marker in tokenish):
                removed += 1
                continue
            clean[key] = _redact_for_archive(item)
        if removed:
            clean["__redacted_sensitive_field_count__"] = removed
        return clean

    if isinstance(value, list):
        return [_redact_for_archive(item) for item in value]

    if isinstance(value, str):
        lowered = value.lower()
        if "tower_keycard=" in lowered or "raw_token" in lowered or "bearer " in lowered:
            return "[REDACTED_SENSITIVE_TEXT]"
    return value


def build_archive_vault_handoff_record(
    *,
    source_type: str,
    source_id: str,
    title: str,
    summary: str,
    severity: str = "medium",
    user_id: str = "owner_solice",
    related_object: Dict[str, Any] | None = None,
    source_payload: Dict[str, Any] | None = None,
    owner_note: str = "",
) -> Dict[str, Any]:
    source_type = _safe_str(source_type, "unknown_source")
    source_id = _safe_str(source_id)
    related_object = related_object if isinstance(related_object, dict) else {}
    source_payload = source_payload if isinstance(source_payload, dict) else {}

    record = {
        "ok": True,
        "handoff_id": "archivehandoff_" + secrets.token_urlsafe(18),
        "event_type": "archive_vault_handoff_request",
        "created_at": _utc_now(),
        "status": "queued",
        "destination": "Archive Vault",
        "source_type": source_type,
        "source_id": source_id,
        "title": _safe_str(title, "Archive Vault evidence handoff"),
        "summary": _safe_str(summary, "Evidence handoff prepared."),
        "severity": _safe_str(severity, "medium"),
        "user_id": _safe_str(user_id, "owner_solice"),
        "owner_note": _safe_str(owner_note),
        "related_object": _redact_for_archive(related_object),
        "source_payload": _redact_for_archive(source_payload),
        "evidence_bundle_stub": {
            "bundle_type": "tower_security_event",
            "chain": [
                "Tower",
                "OB privacy wall",
                "object audit capsule",
                "object security inbox",
                "Archive Vault handoff stub",
            ],
            "ready_for_archive_vault": False,
            "plain": "Archive Vault app is not wired yet. This record is a safe queued handoff stub.",
        },
        "soulaana_translation": "Soulaana: I packaged this security event for the future Archive Vault without exposing secrets.",
        "human_reason": "Archive Vault handoff stub prepared.",
    }

    return record


def queue_archive_vault_handoff(record: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(record, dict):
        return {
            "ok": False,
            "status": "skipped",
            "reason_code": "invalid_archive_handoff_record",
            "human_reason": "Archive Vault handoff record was not a dictionary.",
        }

    existing = _load_json_list(ARCHIVE_HANDOFF_PATH)
    existing.append(_redact_for_archive(record))
    _write_json(ARCHIVE_HANDOFF_PATH, existing)

    return {
        "ok": True,
        "status": "queued",
        "handoff_id": record.get("handoff_id"),
        "path": str(ARCHIVE_HANDOFF_PATH),
        "human_reason": "Archive Vault handoff queued.",
    }


def list_archive_vault_handoffs(limit: int = 25) -> Dict[str, Any]:
    items = _load_json_list(ARCHIVE_HANDOFF_PATH)

    try:
        limit = int(limit)
    except Exception:
        limit = 25
    limit = max(1, min(limit, 500))

    return {
        "ok": True,
        "path": str(ARCHIVE_HANDOFF_PATH),
        "total": len(items),
        "recent": items[-limit:],
        "human_reason": "Archive Vault handoff queue loaded.",
    }


def summarize_archive_vault_handoffs(limit: int = 10) -> Dict[str, Any]:
    items = _load_json_list(ARCHIVE_HANDOFF_PATH)

    by_status: Dict[str, int] = {}
    by_source_type: Dict[str, int] = {}
    by_severity: Dict[str, int] = {}

    for item in items:
        status = _safe_str(item.get("status"), "queued")
        source_type = _safe_str(item.get("source_type"), "unknown")
        severity = _safe_str(item.get("severity"), "unknown")

        by_status[status] = by_status.get(status, 0) + 1
        by_source_type[source_type] = by_source_type.get(source_type, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1

    try:
        limit = int(limit)
    except Exception:
        limit = 10
    limit = max(1, min(limit, 100))

    return {
        "ok": True,
        "path": str(ARCHIVE_HANDOFF_PATH),
        "total": len(items),
        "queued": by_status.get("queued", 0),
        "by_status": by_status,
        "by_source_type": by_source_type,
        "by_severity": by_severity,
        "recent": items[-limit:],
        "human_reason": "Archive Vault handoff summary loaded.",
        "soulaana_translation": "Soulaana: Future evidence bundles are queued safely. The Archive Vault room is not open yet.",
    }


def queue_object_security_event_for_archive(
    *,
    inbox_item: Dict[str, Any],
    actor_user_id: str = "owner_solice",
    owner_note: str = "",
) -> Dict[str, Any]:
    if not isinstance(inbox_item, dict):
        return {
            "ok": False,
            "status": "skipped",
            "reason_code": "invalid_object_inbox_item",
            "human_reason": "Object security inbox item was not a dictionary.",
        }

    object_type = _safe_str(inbox_item.get("object_type"), "object")
    object_id = _safe_str(inbox_item.get("object_id"), "unknown")
    source_id = _safe_str(inbox_item.get("inbox_item_id")) or _safe_str(inbox_item.get("source_capsule_id"))

    record = build_archive_vault_handoff_record(
        source_type="ob_object_security_inbox",
        source_id=source_id,
        title=f"Object security event: {object_type}:{object_id}",
        summary=_safe_str(
            inbox_item.get("soulaana_translation"),
            f"Object security event for {object_type}:{object_id}.",
        ),
        severity=_safe_str(inbox_item.get("severity"), "medium"),
        user_id=_safe_str(actor_user_id, "owner_solice"),
        owner_note=owner_note,
        related_object={
            "object_type": object_type,
            "object_id": object_id,
            "action": inbox_item.get("action"),
            "route_key": inbox_item.get("route_key"),
            "reason_code": inbox_item.get("reason_code"),
            "risk_score": inbox_item.get("risk_score"),
            "risk_state": inbox_item.get("risk_state"),
        },
        source_payload=inbox_item,
    )

    queued = queue_archive_vault_handoff(record)

    return {
        "ok": queued.get("ok") is True,
        "status": queued.get("status"),
        "handoff_id": record.get("handoff_id"),
        "source_id": source_id,
        "path": queued.get("path"),
        "human_reason": "Object security event queued for Archive Vault handoff.",
        "record": record,
    }
