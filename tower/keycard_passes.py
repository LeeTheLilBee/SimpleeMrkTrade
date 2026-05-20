
"""
The Tower — Keycard Passes

This module implements the "key card on every door" security layer.

Core rule:
    Being logged in is NOT enough.

A user/session/device needs a short-lived, scoped, revocable clearance pass for
the exact app, door, object, route, action, or sensitive view being requested.

A pass for one room does not open neighboring rooms.
"""

from __future__ import annotations

import base64
import copy
import dataclasses
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


TOWER_ROOT = Path(__file__).resolve().parent
DATA_DIR = TOWER_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

KEYCARD_REGISTRY_PATH = DATA_DIR / "keycard_passes.json"
KEYCARD_DOOR_LOG_PATH = DATA_DIR / "keycard_door_log.json"

DEFAULT_TTL_SECONDS = 20 * 60

CLEARANCE_RANKS = {
    "public_safe": 0,
    "internal": 10,
    "confidential": 20,
    "restricted": 30,
    "critical": 40,
    "owner_only": 50,
}


# ==============================================================================
# LOW-LEVEL HELPERS
# ==============================================================================

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_iso(value: Any) -> Optional[datetime]:
    if not value:
        return None
    try:
        text = str(value)
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.fromisoformat(text).astimezone(timezone.utc)
    except Exception:
        return None


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _safe_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return copy.deepcopy(default)
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return copy.deepcopy(default)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
    temp_path.replace(path)


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64url_decode(text: str) -> bytes:
    padded = text + ("=" * (-len(text) % 4))
    return base64.urlsafe_b64decode(padded.encode("utf-8"))


def _canonical_json(payload: Dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _get_secret() -> bytes:
    """
    Production should set SIMPLEE_TOWER_KEYCARD_SECRET.

    This fallback is intentionally local/dev-only so tests work in notebooks.
    In deployment, missing env secret should be treated as a launch blocker.
    """
    secret = os.environ.get("SIMPLEE_TOWER_KEYCARD_SECRET", "").strip()
    if secret:
        return secret.encode("utf-8")

    fallback_marker = str(TOWER_ROOT.resolve()).encode("utf-8")
    return hashlib.sha256(b"simplee-dev-keycard-secret:" + fallback_marker).digest()


def _sign_payload(payload: Dict[str, Any]) -> str:
    signature = hmac.new(_get_secret(), _canonical_json(payload), hashlib.sha256).digest()
    return _b64url_encode(signature)


def _token_hash(token: str) -> str:
    return hashlib.sha256(str(token).encode("utf-8")).hexdigest()


def _redact_token(token: str) -> str:
    token = str(token or "")
    if len(token) <= 16:
        return "token_redacted"
    return token[:8] + "..." + token[-8:]


def _load_registry() -> Dict[str, Any]:
    payload = _read_json(KEYCARD_REGISTRY_PATH, {"passes": []})
    if not isinstance(payload, dict):
        payload = {"passes": []}
    if not isinstance(payload.get("passes"), list):
        payload["passes"] = []
    return payload


def _save_registry(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        payload = {"passes": []}
    if not isinstance(payload.get("passes"), list):
        payload["passes"] = []
    payload["updated_at"] = _iso(_utc_now())
    _write_json(KEYCARD_REGISTRY_PATH, payload)


def _append_door_log(event: Dict[str, Any]) -> None:
    log = _read_json(KEYCARD_DOOR_LOG_PATH, {"events": []})
    if not isinstance(log, dict):
        log = {"events": []}
    if not isinstance(log.get("events"), list):
        log["events"] = []

    event = dict(event or {})
    event.setdefault("timestamp", _iso(_utc_now()))
    event.setdefault("event_id", "door_" + secrets.token_urlsafe(18))
    log["events"].append(event)
    log["updated_at"] = _iso(_utc_now())
    _write_json(KEYCARD_DOOR_LOG_PATH, log)


def _decision(
    *,
    allowed: bool,
    reason_code: str,
    human_reason: str,
    risk_state: str = "clear",
    risk_score: int = 0,
    required_actions: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "allowed": bool(allowed),
        "decision": "allow" if allowed else "deny",
        "reason_code": reason_code,
        "human_reason": human_reason,
        "risk_state": risk_state,
        "risk_score": int(risk_score or 0),
        "required_actions": list(required_actions or []),
        "metadata": dict(metadata or {}),
    }


def _rank(clearance_level: str) -> int:
    return CLEARANCE_RANKS.get(str(clearance_level or "internal").strip(), 0)


# ==============================================================================
# DOOR MODEL
# ==============================================================================

@dataclasses.dataclass(frozen=True)
class TowerDoor:
    """
    A TowerDoor is the exact thing someone is trying to open.

    Examples:
        app_name="tower", door_type="route", door_id="/tower/security-command", action="view"
        app_name="observatory", door_type="mode", door_id="paper", action="enter"
        app_name="archive_vault", door_type="record", door_id="capsule_123", action="reveal"
        app_name="simpleepay", door_type="payroll_record", door_id="payroll_2026_05", action="view"
    """

    app_name: str
    door_type: str
    door_id: str
    action: str = "view"
    classification: str = "internal"
    object_owner_user_id: Optional[str] = None
    requires_step_up: bool = False


def make_door(
    app_name: str,
    door_type: str,
    door_id: str,
    action: str = "view",
    classification: str = "internal",
    object_owner_user_id: Optional[str] = None,
    requires_step_up: bool = False,
) -> TowerDoor:
    return TowerDoor(
        app_name=_safe_str(app_name),
        door_type=_safe_str(door_type),
        door_id=_safe_str(door_id),
        action=_safe_str(action, "view"),
        classification=_safe_str(classification, "internal"),
        object_owner_user_id=_safe_str(object_owner_user_id) or None,
        requires_step_up=bool(requires_step_up),
    )


# ==============================================================================
# ISSUE / VALIDATE / REVOKE
# ==============================================================================

def issue_keycard_pass(
    *,
    user_id: str,
    app_name: str,
    door_type: str,
    door_id: str,
    actions: Iterable[str],
    issuer_user_id: str,
    reason: str,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    session_id: Optional[str] = None,
    device_id: Optional[str] = None,
    role: str = "user",
    clearance_level: str = "internal",
    consent_ids: Optional[Iterable[str]] = None,
    risk_score_at_issue: int = 0,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Issue a scoped keycard pass.

    Important:
        The raw token is returned once.
        The registry stores only token_hash, not the token itself.
    """
    user_id = _safe_str(user_id)
    app_name = _safe_str(app_name)
    door_type = _safe_str(door_type)
    door_id = _safe_str(door_id)
    issuer_user_id = _safe_str(issuer_user_id)
    reason = _safe_str(reason)

    if not user_id:
        raise ValueError("user_id is required")
    if not app_name:
        raise ValueError("app_name is required")
    if not door_type:
        raise ValueError("door_type is required")
    if not door_id:
        raise ValueError("door_id is required")
    if not issuer_user_id:
        raise ValueError("issuer_user_id is required")
    if not reason:
        raise ValueError("reason is required to issue a keycard pass")

    action_list = sorted(set(_safe_list(actions)))
    if not action_list:
        raise ValueError("at least one action is required")

    now = _utc_now()
    expires_at = now + timedelta(seconds=int(ttl_seconds))
    pass_id = "kcp_" + secrets.token_urlsafe(18)

    payload = {
        "pass_id": pass_id,
        "user_id": user_id,
        "app_name": app_name,
        "door_type": door_type,
        "door_id": door_id,
        "actions": action_list,
        "issued_at": _iso(now),
        "expires_at": _iso(expires_at),
        "session_id": _safe_str(session_id) or None,
        "device_id": _safe_str(device_id) or None,
        "role": _safe_str(role, "user"),
        "clearance_level": _safe_str(clearance_level, "internal"),
        "consent_ids": sorted(set(_safe_list(consent_ids))),
        "risk_score_at_issue": int(risk_score_at_issue or 0),
    }

    token_body = _b64url_encode(_canonical_json(payload))
    signature = _sign_payload(payload)
    token = f"{token_body}.{signature}"
    hashed = _token_hash(token)

    registry = _load_registry()
    record = {
        **payload,
        "token_hash": hashed,
        "status": "active",
        "issuer_user_id": issuer_user_id,
        "issue_reason": reason,
        "metadata": dict(metadata or {}),
        "revoked_at": None,
        "revoked_by": None,
        "revocation_reason": None,
    }
    registry["passes"].append(record)
    _save_registry(registry)

    _append_door_log({
        "event_type": "keycard_pass_issued",
        "pass_id": pass_id,
        "user_id": user_id,
        "issuer_user_id": issuer_user_id,
        "app_name": app_name,
        "door_type": door_type,
        "door_id": door_id,
        "actions": action_list,
        "clearance_level": payload["clearance_level"],
        "reason": reason,
        "risk_score": int(risk_score_at_issue or 0),
        "token_preview": _redact_token(token),
    })

    return {
        "ok": True,
        "status": "issued",
        "pass_id": pass_id,
        "token": token,
        "token_preview": _redact_token(token),
        "expires_at": payload["expires_at"],
        "human_reason": "Scoped Tower keycard pass issued.",
        "record": copy.deepcopy(record),
    }


def _decode_and_verify_token(token: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    token = _safe_str(token)
    if "." not in token:
        return None, "malformed_token"

    body, signature = token.split(".", 1)
    try:
        payload = json.loads(_b64url_decode(body).decode("utf-8"))
    except Exception:
        return None, "token_payload_unreadable"

    if not isinstance(payload, dict):
        return None, "token_payload_invalid"

    expected = _sign_payload(payload)
    if not hmac.compare_digest(signature, expected):
        return None, "token_signature_invalid"

    return payload, None


def _find_pass_record(pass_id: str, token_hash: str) -> Optional[Dict[str, Any]]:
    registry = _load_registry()
    for record in registry.get("passes", []):
        if not isinstance(record, dict):
            continue
        if record.get("pass_id") == pass_id and record.get("token_hash") == token_hash:
            return record
    return None


def validate_keycard_pass(
    *,
    token: str,
    app_name: str,
    door_type: str,
    door_id: str,
    action: str = "view",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    device_id: Optional[str] = None,
    required_clearance_level: str = "internal",
    required_consent_id: Optional[str] = None,
    current_risk_score: int = 0,
    max_allowed_risk_score: int = 85,
    log_event: bool = True,
) -> Dict[str, Any]:
    """
    Validate whether a token opens this exact door.

    It checks:
        - token format
        - HMAC signature
        - registry match
        - active status
        - expiration
        - exact app
        - exact door type
        - exact door id
        - requested action
        - optional user/session/device binding
        - clearance level
        - consent requirement
        - current risk ceiling
    """
    requested = {
        "app_name": _safe_str(app_name),
        "door_type": _safe_str(door_type),
        "door_id": _safe_str(door_id),
        "action": _safe_str(action, "view"),
        "user_id": _safe_str(user_id) or None,
        "session_id": _safe_str(session_id) or None,
        "device_id": _safe_str(device_id) or None,
        "required_clearance_level": _safe_str(required_clearance_level, "internal"),
        "required_consent_id": _safe_str(required_consent_id) or None,
        "current_risk_score": int(current_risk_score or 0),
        "max_allowed_risk_score": int(max_allowed_risk_score or 0),
    }

    def finish(result: Dict[str, Any]) -> Dict[str, Any]:
        if log_event:
            _append_door_log({
                "event_type": "keycard_pass_validated",
                "allowed": result.get("allowed"),
                "decision": result.get("decision"),
                "reason_code": result.get("reason_code"),
                "human_reason": result.get("human_reason"),
                "requested": requested,
                "pass_id": result.get("metadata", {}).get("pass_id"),
                "token_preview": _redact_token(token),
                "risk_state": result.get("risk_state"),
                "risk_score": result.get("risk_score"),
            })
        return result

    payload, error = _decode_and_verify_token(token)
    if error:
        return finish(_decision(
            allowed=False,
            reason_code=error,
            human_reason="The clearance pass is missing, malformed, or invalid.",
            risk_state="restricted",
            risk_score=75,
            required_actions=["request_new_keycard_pass"],
            metadata={"requested": requested},
        ))

    hashed = _token_hash(token)
    record = _find_pass_record(str(payload.get("pass_id")), hashed)
    if not record:
        return finish(_decision(
            allowed=False,
            reason_code="pass_not_found",
            human_reason="This clearance pass is not recognized by The Tower.",
            risk_state="restricted",
            risk_score=75,
            required_actions=["request_new_keycard_pass"],
            metadata={"requested": requested, "pass_id": payload.get("pass_id")},
        ))

    pass_id = str(record.get("pass_id"))

    if record.get("status") != "active":
        return finish(_decision(
            allowed=False,
            reason_code="pass_not_active",
            human_reason="This clearance pass is no longer active.",
            risk_state="restricted",
            risk_score=70,
            required_actions=["request_new_keycard_pass"],
            metadata={"requested": requested, "pass_id": pass_id, "status": record.get("status")},
        ))

    expires_at = _parse_iso(record.get("expires_at"))
    if not expires_at or expires_at <= _utc_now():
        return finish(_decision(
            allowed=False,
            reason_code="pass_expired",
            human_reason="This clearance pass has expired.",
            risk_state="restricted",
            risk_score=60,
            required_actions=["request_new_keycard_pass"],
            metadata={"requested": requested, "pass_id": pass_id, "expires_at": record.get("expires_at")},
        ))

    checks = [
        ("app_name", "wrong_app", "This pass does not open this app."),
        ("door_type", "wrong_door_type", "This pass does not open this type of door."),
        ("door_id", "wrong_door", "This pass does not open this specific door."),
    ]
    for field, reason_code, human_reason in checks:
        if _safe_str(record.get(field)) != requested[field]:
            return finish(_decision(
                allowed=False,
                reason_code=reason_code,
                human_reason=human_reason,
                risk_state="watch",
                risk_score=45,
                required_actions=["request_correct_keycard_pass"],
                metadata={
                    "requested": requested,
                    "pass_id": pass_id,
                    "pass_scope": {
                        "app_name": record.get("app_name"),
                        "door_type": record.get("door_type"),
                        "door_id": record.get("door_id"),
                    },
                },
            ))

    actions = set(_safe_list(record.get("actions")))
    if requested["action"] not in actions:
        return finish(_decision(
            allowed=False,
            reason_code="action_not_allowed",
            human_reason="This pass does not allow that action.",
            risk_state="watch",
            risk_score=40,
            required_actions=["request_action_clearance"],
            metadata={"requested": requested, "pass_id": pass_id, "pass_actions": sorted(actions)},
        ))

    if requested["user_id"] and _safe_str(record.get("user_id")) != requested["user_id"]:
        return finish(_decision(
            allowed=False,
            reason_code="wrong_user",
            human_reason="This pass belongs to a different user.",
            risk_state="restricted",
            risk_score=80,
            required_actions=["security_review_required"],
            metadata={"requested": requested, "pass_id": pass_id},
        ))

    if requested["session_id"] and record.get("session_id") and record.get("session_id") != requested["session_id"]:
        return finish(_decision(
            allowed=False,
            reason_code="wrong_session",
            human_reason="This pass belongs to a different session.",
            risk_state="restricted",
            risk_score=75,
            required_actions=["step_up_required", "request_new_keycard_pass"],
            metadata={"requested": requested, "pass_id": pass_id},
        ))

    if requested["device_id"] and record.get("device_id") and record.get("device_id") != requested["device_id"]:
        return finish(_decision(
            allowed=False,
            reason_code="wrong_device",
            human_reason="This pass belongs to a different device.",
            risk_state="restricted",
            risk_score=85,
            required_actions=["device_review_required", "request_new_keycard_pass"],
            metadata={"requested": requested, "pass_id": pass_id},
        ))

    pass_clearance = _safe_str(record.get("clearance_level"), "internal")
    if _rank(pass_clearance) < _rank(requested["required_clearance_level"]):
        return finish(_decision(
            allowed=False,
            reason_code="clearance_level_too_low",
            human_reason="This pass does not have enough clearance for this door.",
            risk_state="restricted",
            risk_score=70,
            required_actions=["higher_clearance_required"],
            metadata={
                "requested": requested,
                "pass_id": pass_id,
                "pass_clearance_level": pass_clearance,
            },
        ))

    if requested["required_consent_id"]:
        consent_ids = set(_safe_list(record.get("consent_ids")))
        if requested["required_consent_id"] not in consent_ids:
            return finish(_decision(
                allowed=False,
                reason_code="required_consent_missing",
                human_reason="This pass is missing the required consent acknowledgement.",
                risk_state="restricted",
                risk_score=65,
                required_actions=["complete_required_consent"],
                metadata={
                    "requested": requested,
                    "pass_id": pass_id,
                    "consent_ids": sorted(consent_ids),
                },
            ))

    if requested["current_risk_score"] > requested["max_allowed_risk_score"]:
        return finish(_decision(
            allowed=False,
            reason_code="session_risk_too_high",
            human_reason="Current session risk is too high for this door.",
            risk_state="restricted",
            risk_score=requested["current_risk_score"],
            required_actions=["step_up_required", "security_review_required"],
            metadata={"requested": requested, "pass_id": pass_id},
        ))

    return finish(_decision(
        allowed=True,
        reason_code="keycard_pass_allowed",
        human_reason="This scoped keycard pass opens this exact door.",
        risk_state="clear",
        risk_score=requested["current_risk_score"],
        metadata={
            "pass_id": pass_id,
            "requested": requested,
            "expires_at": record.get("expires_at"),
            "clearance_level": pass_clearance,
            "actions": sorted(actions),
        },
    ))


def validate_door_access(
    *,
    token: str,
    door: TowerDoor,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    device_id: Optional[str] = None,
    current_risk_score: int = 0,
    max_allowed_risk_score: int = 85,
) -> Dict[str, Any]:
    """
    Convenience wrapper for validating a TowerDoor object.
    """
    return validate_keycard_pass(
        token=token,
        app_name=door.app_name,
        door_type=door.door_type,
        door_id=door.door_id,
        action=door.action,
        user_id=user_id,
        session_id=session_id,
        device_id=device_id,
        required_clearance_level=door.classification,
        current_risk_score=current_risk_score,
        max_allowed_risk_score=max_allowed_risk_score,
    )


def revoke_keycard_pass(
    *,
    pass_id: str,
    revoked_by: str,
    reason: str,
) -> Dict[str, Any]:
    pass_id = _safe_str(pass_id)
    revoked_by = _safe_str(revoked_by)
    reason = _safe_str(reason)

    if not pass_id:
        raise ValueError("pass_id is required")
    if not revoked_by:
        raise ValueError("revoked_by is required")
    if not reason:
        raise ValueError("reason is required to revoke a pass")

    registry = _load_registry()
    found = None
    for record in registry.get("passes", []):
        if isinstance(record, dict) and record.get("pass_id") == pass_id:
            found = record
            break

    if not found:
        return {
            "ok": False,
            "status": "not_found",
            "reason_code": "pass_not_found",
            "human_reason": "No matching keycard pass was found.",
            "pass_id": pass_id,
        }

    found["status"] = "revoked"
    found["revoked_at"] = _iso(_utc_now())
    found["revoked_by"] = revoked_by
    found["revocation_reason"] = reason
    _save_registry(registry)

    _append_door_log({
        "event_type": "keycard_pass_revoked",
        "pass_id": pass_id,
        "revoked_by": revoked_by,
        "reason": reason,
        "user_id": found.get("user_id"),
        "app_name": found.get("app_name"),
        "door_type": found.get("door_type"),
        "door_id": found.get("door_id"),
    })

    return {
        "ok": True,
        "status": "revoked",
        "reason_code": "keycard_pass_revoked",
        "human_reason": "Keycard pass revoked.",
        "pass_id": pass_id,
    }


def list_keycard_passes(
    *,
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    app_name: Optional[str] = None,
    include_inactive: bool = True,
) -> Dict[str, Any]:
    registry = _load_registry()
    rows = []
    for record in registry.get("passes", []):
        if not isinstance(record, dict):
            continue
        if status and record.get("status") != status:
            continue
        if user_id and record.get("user_id") != user_id:
            continue
        if app_name and record.get("app_name") != app_name:
            continue
        if not include_inactive and record.get("status") != "active":
            continue

        safe = dict(record)
        safe.pop("token", None)
        safe["token_hash"] = "stored_hash_redacted"
        rows.append(safe)

    return {
        "ok": True,
        "total": len(rows),
        "passes": rows,
    }


def get_keycard_door_log(limit: int = 50) -> Dict[str, Any]:
    log = _read_json(KEYCARD_DOOR_LOG_PATH, {"events": []})
    events = log.get("events", []) if isinstance(log, dict) else []
    if not isinstance(events, list):
        events = []
    limit = max(1, int(limit or 50))
    return {
        "ok": True,
        "total": len(events),
        "events": events[-limit:],
    }


def purge_expired_keycard_passes() -> Dict[str, Any]:
    """
    Mark expired active passes as expired.
    We do not delete by default because security history matters.
    """
    registry = _load_registry()
    changed = 0
    now = _utc_now()

    for record in registry.get("passes", []):
        if not isinstance(record, dict):
            continue
        if record.get("status") != "active":
            continue
        expires_at = _parse_iso(record.get("expires_at"))
        if expires_at and expires_at <= now:
            record["status"] = "expired"
            record["expired_at"] = _iso(now)
            changed += 1

    if changed:
        _save_registry(registry)

    return {
        "ok": True,
        "expired_marked": changed,
        "human_reason": "Expired keycard passes were marked inactive.",
    }


# ==============================================================================
# OPTIONAL WEB HELPERS
# ==============================================================================

def clearance_required_response(reason_code: str = "tower_clearance_required") -> Dict[str, Any]:
    """
    Safe unauthorized response.
    No internal metrics. No app map. No user counts. No route details.
    """
    return {
        "ok": False,
        "reason_code": reason_code,
        "human_reason": "Clearance required.",
    }


def summarize_keycard_health() -> Dict[str, Any]:
    registry = _load_registry()
    passes = [p for p in registry.get("passes", []) if isinstance(p, dict)]
    now = _utc_now()

    active = 0
    expired = 0
    revoked = 0

    for record in passes:
        status = record.get("status")
        if status == "revoked":
            revoked += 1
            continue

        expires_at = _parse_iso(record.get("expires_at"))
        if status == "active" and expires_at and expires_at > now:
            active += 1
        elif expires_at and expires_at <= now:
            expired += 1

    log = _read_json(KEYCARD_DOOR_LOG_PATH, {"events": []})
    events = log.get("events", []) if isinstance(log, dict) else []
    deny_count = 0
    allow_count = 0
    for event in events:
        if not isinstance(event, dict):
            continue
        if event.get("event_type") == "keycard_pass_validated":
            if event.get("allowed"):
                allow_count += 1
            else:
                deny_count += 1

    return {
        "ok": True,
        "keycard_active": active,
        "keycard_expired": expired,
        "keycard_revoked": revoked,
        "keycard_total": len(passes),
        "door_allows_logged": allow_count,
        "door_denies_logged": deny_count,
        "human_reason": "Tower keycard pass health summary loaded.",
    }
