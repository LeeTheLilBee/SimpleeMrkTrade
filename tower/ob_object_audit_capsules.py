
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"
OBJECT_AUDIT_PATH = DATA_DIR / "ob_object_audit_capsules.json"


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


def _redact_tokenish(value: Any) -> Any:
    """Remove tokenish fields so secret field names and values do not survive.

    Baby version:
    If a key smells like a token/keycard/secret/password, we do not keep the key.
    We only keep a generic count saying sensitive fields were removed.
    """
    tokenish_markers = ["token", "keycard", "secret", "password", "authorization", "auth_header", "bearer"]

    if isinstance(value, dict):
        clean = {}
        removed_count = 0

        for key, item in value.items():
            key_text = str(key).lower()
            if any(bad in key_text for bad in tokenish_markers):
                removed_count += 1
                continue

            cleaned_item = _redact_tokenish(item)
            clean[key] = cleaned_item

        if removed_count:
            clean["__redacted_sensitive_field_count__"] = removed_count

        return clean

    if isinstance(value, list):
        return [_redact_tokenish(item) for item in value]

    if isinstance(value, str):
        lowered = value.lower()
        if "tower_keycard=" in lowered or "raw_token" in lowered or "bearer " in lowered:
            return "[REDACTED_SENSITIVE_TEXT]"

    return value


def _fingerprint(payload: Dict[str, Any]) -> str:
    safe_payload = _redact_tokenish(payload)
    raw = json.dumps(safe_payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:28]


def _severity_for_decision(decision: Dict[str, Any]) -> str:
    reason = _safe_str(decision.get("reason_code")).lower()
    risk_score = _safe_int(decision.get("risk_score"), 0)
    allowed = bool(decision.get("allowed"))
    action = _safe_str(decision.get("metadata", {}).get("action") if isinstance(decision.get("metadata"), dict) else "").lower()

    if allowed:
        if action in {"download", "export", "change", "execute"}:
            return "info_watch"
        return "info"

    if "unmapped" in reason:
        return "high"
    if "risk_too_high" in reason or decision.get("decision") == "step_up":
        return "high"
    if "export" in reason or action in {"download", "export"}:
        return "high"
    if risk_score >= 80:
        return "high"
    if risk_score >= 60:
        return "medium"
    return "low"


def _soulaana_translation(
    *,
    allowed: bool,
    object_type: str,
    object_id: str,
    reason_code: str,
    action: str,
) -> str:
    pretty_object = f"{object_type}:{object_id}" if object_id else object_type

    if allowed:
        return f"Soulaana: {pretty_object} was opened for {action}. The drawer cleared, and the receipt is filed."

    if reason_code == "ob_object_unmapped_default_deny":
        return f"Soulaana: {pretty_object} is not on the drawer map. I kept it locked and filed the receipt."

    if reason_code == "parent_route_clearance_failed":
        return f"Soulaana: {pretty_object} could not open because the hallway failed first. Receipt filed."

    if "risk" in reason_code or "step_up" in reason_code:
        return f"Soulaana: {pretty_object} hit risk weather. I stopped the reveal and filed the receipt."

    return f"Soulaana: {pretty_object} did not clear for {action}. No reveal. Receipt filed."


def record_ob_object_audit_capsule(
    *,
    decision: Dict[str, Any],
    object_kind: str = "",
    object_type: str = "",
    object_id: str = "",
    action: str = "",
    route_key: str = "",
    user_id: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    metadata = metadata if isinstance(metadata, dict) else {}
    decision = decision if isinstance(decision, dict) else {}

    decision_metadata = decision.get("metadata") if isinstance(decision.get("metadata"), dict) else {}

    final_object_type = _safe_str(object_type, _safe_str(decision_metadata.get("object_type"), _safe_str(object_kind, "object")))
    final_object_id = _safe_str(object_id, _safe_str(decision_metadata.get("object_id"), ""))
    final_action = _safe_str(action, _safe_str(decision_metadata.get("action"), "view"))
    final_route_key = _safe_str(route_key, _safe_str(decision_metadata.get("route_key"), ""))
    final_user_id = _safe_str(user_id, _safe_str(decision_metadata.get("user_id"), "anonymous"))

    allowed = bool(decision.get("allowed"))
    reason_code = _safe_str(decision.get("reason_code"), "unknown_object_decision")
    severity = _severity_for_decision(decision)

    base_for_fingerprint = {
        "user_id": final_user_id,
        "object_type": final_object_type,
        "object_id": final_object_id,
        "action": final_action,
        "route_key": final_route_key,
        "allowed": allowed,
        "reason_code": reason_code,
        "risk_score": decision.get("risk_score"),
        "risk_state": decision.get("risk_state"),
    }

    capsule = {
        "ok": True,
        "capsule_id": "objcaps_" + secrets.token_urlsafe(18),
        "event_type": "ob_object_guard_audit_capsule",
        "created_at": _utc_now(),
        "user_id": final_user_id,
        "object_kind": _safe_str(object_kind, final_object_type),
        "object_type": final_object_type,
        "object_id": final_object_id,
        "action": final_action,
        "route_key": final_route_key,
        "allowed": allowed,
        "decision": _safe_str(decision.get("decision"), "unknown"),
        "reason_code": reason_code,
        "risk_score": _safe_int(decision.get("risk_score"), 0),
        "risk_state": _safe_str(decision.get("risk_state"), "unknown"),
        "severity": severity,
        "required_actions": decision.get("required_actions") if isinstance(decision.get("required_actions"), list) else [],
        "human_reason": _safe_str(decision.get("human_reason"), "Object guard decision recorded."),
        "soulaana_translation": _soulaana_translation(
            allowed=allowed,
            object_type=final_object_type,
            object_id=final_object_id,
            reason_code=reason_code,
            action=final_action,
        ),
        "source_fingerprint": _fingerprint(base_for_fingerprint),
        "metadata": _redact_tokenish({
            "pack": "056",
            "guard_metadata": metadata,
            "decision_metadata": decision_metadata,
        }),
    }

    existing = _load_json_list(OBJECT_AUDIT_PATH)
    existing.append(capsule)
    _write_json(OBJECT_AUDIT_PATH, existing)

    # PACK058_AUTO_BRIDGE_OBJECT_CAPSULE
    try:
        bridge_result = bridge_object_capsule_to_security_inbox(capsule)
        capsule["object_security_inbox_bridge"] = bridge_result
    except Exception as bridge_error:
        capsule["object_security_inbox_bridge"] = {
            "ok": False,
            "status": "error",
            "reason_code": "object_security_inbox_bridge_error",
            "human_reason": str(bridge_error),
        }

    return capsule


def list_ob_object_audit_capsules(limit: int = 25) -> Dict[str, Any]:
    items = _load_json_list(OBJECT_AUDIT_PATH)
    try:
        limit = int(limit)
    except Exception:
        limit = 25
    limit = max(1, min(limit, 500))

    return {
        "ok": True,
        "path": str(OBJECT_AUDIT_PATH),
        "total": len(items),
        "recent": items[-limit:],
        "human_reason": "OB object audit capsules loaded.",
    }


def summarize_ob_object_audit_capsules(limit: int = 10) -> Dict[str, Any]:
    items = _load_json_list(OBJECT_AUDIT_PATH)

    by_reason: Dict[str, int] = {}
    by_object_type: Dict[str, int] = {}
    by_severity: Dict[str, int] = {}
    by_allowed = {"allowed": 0, "denied": 0}

    for item in items:
        reason = _safe_str(item.get("reason_code"), "unknown")
        object_type = _safe_str(item.get("object_type"), "unknown")
        severity = _safe_str(item.get("severity"), "unknown")
        by_reason[reason] = by_reason.get(reason, 0) + 1
        by_object_type[object_type] = by_object_type.get(object_type, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1
        if item.get("allowed"):
            by_allowed["allowed"] += 1
        else:
            by_allowed["denied"] += 1

    try:
        limit = int(limit)
    except Exception:
        limit = 10
    limit = max(1, min(limit, 100))

    return {
        "ok": True,
        "path": str(OBJECT_AUDIT_PATH),
        "total": len(items),
        "allowed": by_allowed["allowed"],
        "denied": by_allowed["denied"],
        "by_reason": by_reason,
        "by_object_type": by_object_type,
        "by_severity": by_severity,
        "recent": items[-limit:],
        "human_reason": "OB object audit capsule summary loaded.",
        "soulaana_translation": "Soulaana: The drawer receipts are counted. Every object touch has a paper trail.",
    }



# ================================================================================
# PACK058_OBJECT_AUDIT_SECURITY_INBOX_BRIDGE
# ================================================================================
# Converts review-worthy object audit capsules into actionable security inbox items.
# ================================================================================

OBJECT_SECURITY_INBOX_PATH = DATA_DIR / "ob_object_security_inbox.json"


def _pack058_should_bridge_object_capsule(capsule: Dict[str, Any]) -> bool:
    try:
        if not isinstance(capsule, dict):
            return False

        allowed = bool(capsule.get("allowed"))
        reason_code = _safe_str(capsule.get("reason_code")).lower()
        severity = _safe_str(capsule.get("severity")).lower()
        action = _safe_str(capsule.get("action")).lower()
        object_type = _safe_str(capsule.get("object_type")).lower()

        # Normal allowed views stay quiet.
        if allowed and action in {"view", "enter"} and severity in {"info", "info_watch"}:
            return False

        # Review-worthy buckets.
        if not allowed:
            return True
        if severity in {"high", "critical"}:
            return True
        if "unmapped" in reason_code:
            return True
        if "risk" in reason_code or "step_up" in reason_code:
            return True
        if action in {"download", "export", "change", "execute"}:
            return True
        if object_type in {"export", "admin_control", "account"} and not allowed:
            return True

        return False
    except Exception:
        return False


def _pack058_inbox_item_exists(source_capsule_id: str) -> bool:
    source_capsule_id = _safe_str(source_capsule_id)
    if not source_capsule_id:
        return False

    existing = _load_json_list(OBJECT_SECURITY_INBOX_PATH)
    for item in existing:
        if _safe_str(item.get("source_capsule_id")) == source_capsule_id:
            return True
    return False


def _pack058_owner_action_for_capsule(capsule: Dict[str, Any]) -> str:
    object_type = _safe_str(capsule.get("object_type"), "object")
    object_id = _safe_str(capsule.get("object_id"), "unknown")
    reason = _safe_str(capsule.get("reason_code"), "unknown_reason")
    action = _safe_str(capsule.get("action"), "view")

    if reason == "ob_object_unmapped_default_deny":
        return f"Review whether {object_type}:{object_id} should be mapped into the object guard policy."

    if object_type == "export" or action in {"download", "export"}:
        return f"Review attempted export/download {object_id}. Confirm whether this was authorized."

    if "risk" in reason or "step_up" in reason:
        return f"Review risk/step-up event for {object_type}:{object_id}."

    if reason == "parent_route_clearance_failed":
        return f"Review blocked object access for {object_type}:{object_id}; the parent route failed first."

    return f"Review object access event for {object_type}:{object_id}."


def bridge_object_capsule_to_security_inbox(capsule: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(capsule, dict):
        return {
            "ok": False,
            "status": "skipped",
            "reason_code": "invalid_capsule",
            "human_reason": "Object audit capsule was not a dictionary.",
        }

    capsule_id = _safe_str(capsule.get("capsule_id"))
    if not capsule_id:
        return {
            "ok": False,
            "status": "skipped",
            "reason_code": "missing_capsule_id",
            "human_reason": "Object audit capsule had no capsule ID.",
        }

    if not _pack058_should_bridge_object_capsule(capsule):
        return {
            "ok": True,
            "status": "quiet",
            "reason_code": "object_capsule_not_review_worthy",
            "source_capsule_id": capsule_id,
            "human_reason": "Object audit capsule did not need security inbox review.",
        }

    if _pack058_inbox_item_exists(capsule_id):
        return {
            "ok": True,
            "status": "already_exists",
            "reason_code": "object_inbox_item_already_exists",
            "source_capsule_id": capsule_id,
            "human_reason": "Security inbox item already exists for this object capsule.",
        }

    existing = _load_json_list(OBJECT_SECURITY_INBOX_PATH)

    object_type = _safe_str(capsule.get("object_type"), "object")
    object_id = _safe_str(capsule.get("object_id"), "unknown")
    reason_code = _safe_str(capsule.get("reason_code"), "unknown_reason")
    severity = _safe_str(capsule.get("severity"), "medium")
    action = _safe_str(capsule.get("action"), "view")
    user_id = _safe_str(capsule.get("user_id"), "anonymous")

    item = {
        "ok": True,
        "inbox_item_id": "objinbox_" + secrets.token_urlsafe(18),
        "event_type": "ob_object_security_review",
        "created_at": _utc_now(),
        "updated_at": "",
        "status": "open",
        "surface": "object_security_inbox",
        "source_capsule_id": capsule_id,
        "source_fingerprint": _safe_str(capsule.get("source_fingerprint"), ""),
        "user_id": user_id,
        "object_kind": _safe_str(capsule.get("object_kind"), object_type),
        "object_type": object_type,
        "object_id": object_id,
        "action": action,
        "route_key": _safe_str(capsule.get("route_key"), ""),
        "allowed": bool(capsule.get("allowed")),
        "reason_code": reason_code,
        "risk_score": _safe_int(capsule.get("risk_score"), 0),
        "risk_state": _safe_str(capsule.get("risk_state"), "unknown"),
        "severity": severity,
        "title": f"OB object review: {reason_code} at {object_type}:{object_id}",
        "owner_action": _pack058_owner_action_for_capsule(capsule),
        "soulaana_translation": _safe_str(
            capsule.get("soulaana_translation"),
            f"Soulaana: {object_type}:{object_id} needs review.",
        ),
        "routing": {
            "queue": "ob_object_security_inbox",
            "surface": "watchlist",
            "requires_step_up_review": severity in {"high", "critical"},
        },
        "owner_notes": [],
        "history": [],
    }

    existing.append(item)
    _write_json(OBJECT_SECURITY_INBOX_PATH, existing)

    return {
        "ok": True,
        "status": "created",
        "reason_code": "object_security_inbox_item_created",
        "source_capsule_id": capsule_id,
        "inbox_item_id": item.get("inbox_item_id"),
        "human_reason": "Review-worthy object audit capsule bridged into security inbox.",
    }


def bridge_recent_object_audit_capsules_to_security_inbox(limit: int = 100) -> Dict[str, Any]:
    audit_items = _load_json_list(OBJECT_AUDIT_PATH)
    try:
        limit = int(limit)
    except Exception:
        limit = 100
    limit = max(1, min(limit, 1000))

    recent = audit_items[-limit:]

    created = 0
    quiet = 0
    already_exists = 0
    skipped = 0
    results = []

    for capsule in recent:
        result = bridge_object_capsule_to_security_inbox(capsule)
        results.append(result)

        status = _safe_str(result.get("status"))
        if status == "created":
            created += 1
        elif status == "quiet":
            quiet += 1
        elif status == "already_exists":
            already_exists += 1
        else:
            skipped += 1

    return {
        "ok": True,
        "created": created,
        "quiet": quiet,
        "already_exists": already_exists,
        "skipped": skipped,
        "checked": len(recent),
        "results": results[-25:],
        "human_reason": "Recent object audit capsules bridged into security inbox where review-worthy.",
    }


def list_ob_object_security_inbox(limit: int = 25, include_resolved: bool = True) -> Dict[str, Any]:
    items = _load_json_list(OBJECT_SECURITY_INBOX_PATH)

    if not include_resolved:
        items = [item for item in items if _safe_str(item.get("status"), "open") in {"open", "reviewing"}]

    try:
        limit = int(limit)
    except Exception:
        limit = 25
    limit = max(1, min(limit, 500))

    return {
        "ok": True,
        "path": str(OBJECT_SECURITY_INBOX_PATH),
        "total": len(items),
        "recent": items[-limit:],
        "human_reason": "OB object security inbox loaded.",
    }


def summarize_ob_object_security_inbox(limit: int = 10) -> Dict[str, Any]:
    items = _load_json_list(OBJECT_SECURITY_INBOX_PATH)

    by_status: Dict[str, int] = {}
    by_reason: Dict[str, int] = {}
    by_severity: Dict[str, int] = {}
    by_object_type: Dict[str, int] = {}

    open_count = 0

    for item in items:
        status = _safe_str(item.get("status"), "open")
        reason = _safe_str(item.get("reason_code"), "unknown")
        severity = _safe_str(item.get("severity"), "unknown")
        object_type = _safe_str(item.get("object_type"), "unknown")

        by_status[status] = by_status.get(status, 0) + 1
        by_reason[reason] = by_reason.get(reason, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_object_type[object_type] = by_object_type.get(object_type, 0) + 1

        if status in {"open", "reviewing"}:
            open_count += 1

    try:
        limit = int(limit)
    except Exception:
        limit = 10
    limit = max(1, min(limit, 100))

    return {
        "ok": True,
        "path": str(OBJECT_SECURITY_INBOX_PATH),
        "total": len(items),
        "open": open_count,
        "by_status": by_status,
        "by_reason": by_reason,
        "by_severity": by_severity,
        "by_object_type": by_object_type,
        "recent": items[-limit:],
        "human_reason": "OB object security inbox summary loaded.",
        "soulaana_translation": "Soulaana: Review-worthy drawer events are now in the owner's queue.",
    }

