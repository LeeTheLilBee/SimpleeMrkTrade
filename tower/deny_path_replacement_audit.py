
from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"
DENY_PATH_REPLACEMENT_AUDIT_PATH = DATA_DIR / "deny_path_replacement_audit_receipts.json"


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


def record_deny_path_replacement_receipt(
    *,
    route_path: str,
    replacement_type: str = "polished_tower_locked_page",
    old_behavior: str = "legacy_locked_shell",
    new_behavior: str = "tower_polished_locked_helper",
    actor_user_id: str = "owner_solice",
    reason: str = "",
    proof: Dict[str, Any] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    proof = proof if isinstance(proof, dict) else {}
    metadata = metadata if isinstance(metadata, dict) else {}

    proof_clean = _redact(proof)
    metadata_clean = _redact(metadata)

    proof_ok = bool(proof_clean.get("ok", False))
    status_code = _safe_int(proof_clean.get("status_code"), 0)

    if proof_ok and status_code == 403:
        severity = "info"
        risk_state = "clear"
        risk_score = 10
        status = "verified"
    elif proof_ok:
        severity = "low"
        risk_state = "watch"
        risk_score = 35
        status = "partial"
    else:
        severity = "medium"
        risk_state = "watch"
        risk_score = 55
        status = "needs_review"

    receipt = {
        "ok": True,
        "receipt_id": "denyreplace_" + secrets.token_urlsafe(18),
        "event_type": "deny_path_replacement_audit_receipt",
        "created_at": _utc_now(),
        "status": status,
        "route_path": _safe_str(route_path),
        "replacement_type": _safe_str(replacement_type, "polished_tower_locked_page"),
        "old_behavior": _safe_str(old_behavior, "legacy_locked_shell"),
        "new_behavior": _safe_str(new_behavior, "tower_polished_locked_helper"),
        "actor_user_id": _safe_str(actor_user_id, "owner_solice"),
        "reason": _safe_str(reason, "Deny path replacement recorded."),
        "proof": proof_clean,
        "metadata": metadata_clean,
        "severity": severity,
        "risk_state": risk_state,
        "risk_score": risk_score,
        "soulaana_translation": (
            "Soulaana: Deny-path replacement receipt filed. The locked door changed, and the proof is attached."
            if status == "verified"
            else "Soulaana: Deny-path replacement needs review before we trust it fully."
        ),
        "human_reason": "Deny-path replacement audit receipt recorded.",
    }

    items = _load_json_list(DENY_PATH_REPLACEMENT_AUDIT_PATH)
    items.append(receipt)
    _write_json(DENY_PATH_REPLACEMENT_AUDIT_PATH, items)

    return receipt


def list_deny_path_replacement_receipts(limit: int = 25) -> Dict[str, Any]:
    items = _load_json_list(DENY_PATH_REPLACEMENT_AUDIT_PATH)

    try:
        limit = int(limit)
    except Exception:
        limit = 25
    limit = max(1, min(limit, 500))

    return {
        "ok": True,
        "path": str(DENY_PATH_REPLACEMENT_AUDIT_PATH),
        "total": len(items),
        "recent": items[-limit:],
        "human_reason": "Deny-path replacement audit receipts loaded.",
    }


def summarize_deny_path_replacement_receipts(limit: int = 10) -> Dict[str, Any]:
    items = _load_json_list(DENY_PATH_REPLACEMENT_AUDIT_PATH)

    by_status: Dict[str, int] = {}
    by_route: Dict[str, int] = {}
    by_replacement_type: Dict[str, int] = {}
    by_severity: Dict[str, int] = {}
    verified = 0
    needs_review = 0

    for item in items:
        status = _safe_str(item.get("status"), "unknown")
        route = _safe_str(item.get("route_path"), "unknown")
        replacement_type = _safe_str(item.get("replacement_type"), "unknown")
        severity = _safe_str(item.get("severity"), "unknown")

        by_status[status] = by_status.get(status, 0) + 1
        by_route[route] = by_route.get(route, 0) + 1
        by_replacement_type[replacement_type] = by_replacement_type.get(replacement_type, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1

        if status == "verified":
            verified += 1
        elif status == "needs_review":
            needs_review += 1

    try:
        limit = int(limit)
    except Exception:
        limit = 10
    limit = max(1, min(limit, 100))

    return {
        "ok": True,
        "path": str(DENY_PATH_REPLACEMENT_AUDIT_PATH),
        "total": len(items),
        "verified": verified,
        "needs_review": needs_review,
        "by_status": by_status,
        "by_route": by_route,
        "by_replacement_type": by_replacement_type,
        "by_severity": by_severity,
        "recent": items[-limit:],
        "human_reason": "Deny-path replacement audit receipt summary loaded.",
        "soulaana_translation": "Soulaana: Replacement receipts are counted. Every changed locked door gets a paper trail.",
    }
