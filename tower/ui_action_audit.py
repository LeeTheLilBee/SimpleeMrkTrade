
from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"
UI_ACTION_AUDIT_PATH = DATA_DIR / "ui_action_audit_receipts.json"


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


def _redact(value: Any) -> Any:
    secret_markers = [
        "tower_keycard",
        "raw_token",
        "token",
        "password",
        "secret",
        "authorization",
        "bearer",
    ]

    if isinstance(value, dict):
        clean = {}
        removed = 0
        for key, item in value.items():
            key_text = str(key).lower()
            if any(marker in key_text for marker in secret_markers):
                removed += 1
                continue
            clean[key] = _redact(item)
        if removed:
            clean["__redacted_sensitive_field_count__"] = removed
        return clean

    if isinstance(value, list):
        return [_redact(item) for item in value]

    if isinstance(value, str):
        lowered = value.lower()
        if "tower_keycard=" in lowered or "raw_token" in lowered or "bearer " in lowered:
            return "[REDACTED_SENSITIVE_TEXT]"
        if "should_not_survive" in lowered:
            return "[REDACTED_TEST_SECRET]"
    return value


def record_ui_action_audit_receipt(
    *,
    endpoint: str,
    action_type: str,
    actor_user_id: str = "owner_solice",
    inbox_item_id: str = "",
    ok: bool = False,
    status_code: int = 200,
    reason_code: str = "",
    human_reason: str = "",
    request_payload: Dict[str, Any] | None = None,
    result_payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    request_payload = request_payload if isinstance(request_payload, dict) else {}
    result_payload = result_payload if isinstance(result_payload, dict) else {}

    ok_bool = bool(ok)
    status_code_int = _safe_int(status_code, 200 if ok_bool else 400)

    if ok_bool:
        severity = "info"
        risk_state = "clear"
        risk_score = 10
    elif status_code_int >= 500:
        severity = "high"
        risk_state = "restricted"
        risk_score = 80
    elif status_code_int >= 400:
        severity = "medium"
        risk_state = "watch"
        risk_score = 55
    else:
        severity = "low"
        risk_state = "watch"
        risk_score = 35

    receipt = {
        "ok": True,
        "receipt_id": "uiaudit_" + secrets.token_urlsafe(18),
        "event_type": "tower_ui_action_audit_receipt",
        "created_at": _utc_now(),
        "endpoint": _safe_str(endpoint),
        "action_type": _safe_str(action_type),
        "actor_user_id": _safe_str(actor_user_id, "owner_solice"),
        "inbox_item_id": _safe_str(inbox_item_id),
        "action_ok": ok_bool,
        "status_code": status_code_int,
        "reason_code": _safe_str(reason_code, "ui_action_processed" if ok_bool else "ui_action_failed"),
        "human_reason": _safe_str(human_reason, "Tower UI action audit receipt recorded."),
        "severity": severity,
        "risk_state": risk_state,
        "risk_score": risk_score,
        "request_payload": _redact(request_payload),
        "result_payload": _redact(result_payload),
        "soulaana_translation": (
            "Soulaana: Owner UI action recorded. The button click has a receipt."
            if ok_bool
            else "Soulaana: UI action did not clear cleanly. I recorded the attempt."
        ),
    }

    items = _load_json_list(UI_ACTION_AUDIT_PATH)
    items.append(receipt)
    _write_json(UI_ACTION_AUDIT_PATH, items)

    return receipt


def list_ui_action_audit_receipts(limit: int = 25) -> Dict[str, Any]:
    items = _load_json_list(UI_ACTION_AUDIT_PATH)

    try:
        limit = int(limit)
    except Exception:
        limit = 25
    limit = max(1, min(limit, 500))

    return {
        "ok": True,
        "path": str(UI_ACTION_AUDIT_PATH),
        "total": len(items),
        "recent": items[-limit:],
        "human_reason": "Tower UI action audit receipts loaded.",
    }


def summarize_ui_action_audit_receipts(limit: int = 10) -> Dict[str, Any]:
    items = _load_json_list(UI_ACTION_AUDIT_PATH)

    by_action: Dict[str, int] = {}
    by_reason: Dict[str, int] = {}
    by_severity: Dict[str, int] = {}
    by_status_code: Dict[str, int] = {}
    ok_count = 0
    failed_count = 0

    for item in items:
        action = _safe_str(item.get("action_type"), "unknown")
        reason = _safe_str(item.get("reason_code"), "unknown")
        severity = _safe_str(item.get("severity"), "unknown")
        status_code = str(_safe_int(item.get("status_code"), 0))

        by_action[action] = by_action.get(action, 0) + 1
        by_reason[reason] = by_reason.get(reason, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_status_code[status_code] = by_status_code.get(status_code, 0) + 1

        if item.get("action_ok") is True:
            ok_count += 1
        else:
            failed_count += 1

    try:
        limit = int(limit)
    except Exception:
        limit = 10
    limit = max(1, min(limit, 100))

    return {
        "ok": True,
        "path": str(UI_ACTION_AUDIT_PATH),
        "total": len(items),
        "action_ok": ok_count,
        "action_failed": failed_count,
        "by_action": by_action,
        "by_reason": by_reason,
        "by_severity": by_severity,
        "by_status_code": by_status_code,
        "recent": items[-limit:],
        "human_reason": "Tower UI action audit receipt summary loaded.",
        "soulaana_translation": "Soulaana: The owner button clicks are counted. Every action leaves a receipt.",
    }
