# =============================================================================
# THE TOWER — CLEARANCE TOKENS
# FILE: tower/clearance_tokens.py
# =============================================================================

import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, List

from tower.audit import write_audit_event
from tower.security_events import create_security_event


PROJECT_ROOT = os.environ.get("SIMPLEE_PROJECT_ROOT", "/content/SimpleeMrkTrade_REAL_CLONE")
TOWER_DATA_DIR = Path(PROJECT_ROOT) / "tower" / "data"
TOKENS_PATH = TOWER_DATA_DIR / "clearance_tokens.json"

TOWER_DATA_DIR.mkdir(parents=True, exist_ok=True)


# For now this is local-dev only.
# Later this should come from a real secret manager / environment variable.
TOWER_TOKEN_SECRET = os.environ.get(
    "TOWER_TOKEN_SECRET",
    "DEV_ONLY_CHANGE_ME_BEFORE_PRODUCTION"
)


def _now_dt() -> datetime:
    return datetime.utcnow()


def _now() -> str:
    return _now_dt().isoformat() + "Z"


def _expires(minutes: int = 15) -> str:
    return (_now_dt() + timedelta(minutes=minutes)).isoformat() + "Z"


def _load_raw() -> Dict[str, Any]:
    if not TOKENS_PATH.exists():
        return {"tokens": []}

    try:
        with TOKENS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return {"tokens": []}

        if not isinstance(data.get("tokens"), list):
            data["tokens"] = []

        return data
    except Exception:
        return {"tokens": []}


def _save_raw(data: Dict[str, Any]) -> None:
    tmp_path = TOKENS_PATH.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True, default=str)

    tmp_path.replace(TOKENS_PATH)


def _safe_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _sign_payload(payload: Dict[str, Any]) -> str:
    raw = _safe_json(payload).encode("utf-8")
    secret = TOWER_TOKEN_SECRET.encode("utf-8")
    return hmac.new(secret, raw, hashlib.sha256).hexdigest()


def _parse_time(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None

    try:
        return datetime.fromisoformat(str(value).replace("Z", ""))
    except Exception:
        return None


def issue_clearance_token(
    user_id: str,
    app_name: str,
    action: str = "enter_app",
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    scope: Optional[str] = None,
    minutes_valid: int = 15,
    issued_by: str = "tower",
    reason_code: str = "clearance_token_issued",
    risk_state: str = "clear",
    risk_score: int = 10,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Issues a short-lived Tower pass.

    Baby version:
    This gives the app a temporary permission slip.
    """

    metadata = metadata or {}

    token_id = secrets.token_urlsafe(18)
    issued_at = _now()
    expires_at = _expires(minutes_valid)

    payload = {
        "token_id": token_id,
        "user_id": user_id,
        "app_name": app_name,
        "action": action,
        "mode_name": mode_name,
        "object_type": object_type,
        "object_id": object_id,
        "scope": scope or f"{app_name}:{action}:{mode_name or '*'}",
        "issued_at": issued_at,
        "expires_at": expires_at,
        "issued_by": issued_by,
        "risk_state": risk_state,
        "risk_score": risk_score,
    }

    signature = _sign_payload(payload)

    record = dict(payload)
    record["signature"] = signature
    record["status"] = "active"
    record["revoked_at"] = None
    record["revoked_by"] = None
    record["revoke_reason"] = None
    record["metadata"] = metadata

    data = _load_raw()
    data["tokens"].append(record)
    _save_raw(data)

    write_audit_event(
        actor_user_id=issued_by,
        target_user_id=user_id,
        action="issue_clearance_token",
        app_name="tower_admin",
        object_type="clearance_token",
        object_id=token_id,
        result="allow",
        reason_code=reason_code,
        human_reason="Tower clearance token was issued.",
        risk_score=risk_score,
        risk_state=risk_state,
        metadata={
            "token_id": token_id,
            "scope": record.get("scope"),
            "app_name": app_name,
            "mode_name": mode_name,
            "expires_at": expires_at,
        },
    )

    return record


def get_clearance_token(token_id: str) -> Optional[Dict[str, Any]]:
    data = _load_raw()

    for token in data.get("tokens", []):
        if token.get("token_id") == token_id:
            return token

    return None


def validate_clearance_token(
    token_id: str,
    user_id: Optional[str] = None,
    app_name: Optional[str] = None,
    action: Optional[str] = None,
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    write_audit: bool = True,
) -> Dict[str, Any]:
    """
    Validates a Tower pass.

    Baby version:
    This checks if the pass is real, not expired, not revoked,
    and belongs to the right user/app/door.
    """

    token = get_clearance_token(token_id)

    if not token:
        result = {
            "valid": False,
            "reason_code": "clearance_token_not_found",
            "human_reason": "Clearance token was not found.",
            "token_id": token_id,
        }

        if write_audit:
            write_audit_event(
                actor_user_id=user_id or "unknown",
                action="validate_clearance_token",
                app_name=app_name,
                object_type="clearance_token",
                object_id=token_id,
                result="deny",
                reason_code=result["reason_code"],
                human_reason=result["human_reason"],
                risk_score=80,
                risk_state="restricted",
                metadata=result,
            )

        return result

    signature = token.get("signature")
    payload = {
        "token_id": token.get("token_id"),
        "user_id": token.get("user_id"),
        "app_name": token.get("app_name"),
        "action": token.get("action"),
        "mode_name": token.get("mode_name"),
        "object_type": token.get("object_type"),
        "object_id": token.get("object_id"),
        "scope": token.get("scope"),
        "issued_at": token.get("issued_at"),
        "expires_at": token.get("expires_at"),
        "issued_by": token.get("issued_by"),
        "risk_state": token.get("risk_state"),
        "risk_score": token.get("risk_score"),
    }

    expected_signature = _sign_payload(payload)

    if not hmac.compare_digest(str(signature), str(expected_signature)):
        create_security_event(
            user_id=str(token.get("user_id", "unknown")),
            event_type="clearance_token_signature_mismatch",
            severity="critical",
            source_app=token.get("app_name"),
            description="A clearance token signature did not match.",
            recommended_action="revoke_token_and_review_session",
            metadata={"token_id": token_id},
        )

        return {
            "valid": False,
            "reason_code": "clearance_token_signature_mismatch",
            "human_reason": "Clearance token signature is invalid.",
            "token_id": token_id,
        }

    if token.get("status") != "active":
        return {
            "valid": False,
            "reason_code": "clearance_token_not_active",
            "human_reason": "Clearance token is not active.",
            "token_id": token_id,
            "status": token.get("status"),
        }

    expires_at = _parse_time(token.get("expires_at"))
    if not expires_at or expires_at < _now_dt():
        return {
            "valid": False,
            "reason_code": "clearance_token_expired",
            "human_reason": "Clearance token is expired.",
            "token_id": token_id,
            "expires_at": token.get("expires_at"),
        }

    checks = [
        ("user_id", user_id),
        ("app_name", app_name),
        ("action", action),
        ("mode_name", mode_name),
        ("object_type", object_type),
        ("object_id", object_id),
    ]

    for key, expected in checks:
        if expected is None:
            continue

        actual = token.get(key)

        if str(actual) != str(expected):
            return {
                "valid": False,
                "reason_code": f"clearance_token_{key}_mismatch",
                "human_reason": f"Clearance token does not match expected {key}.",
                "token_id": token_id,
                "expected": expected,
                "actual": actual,
            }

    return {
        "valid": True,
        "reason_code": "clearance_token_valid",
        "human_reason": "Clearance token is valid.",
        "token_id": token_id,
        "user_id": token.get("user_id"),
        "app_name": token.get("app_name"),
        "action": token.get("action"),
        "mode_name": token.get("mode_name"),
        "object_type": token.get("object_type"),
        "object_id": token.get("object_id"),
        "scope": token.get("scope"),
        "expires_at": token.get("expires_at"),
        "risk_state": token.get("risk_state"),
        "risk_score": token.get("risk_score"),
    }


def revoke_clearance_token(
    token_id: str,
    revoked_by: str,
    reason: str = "clearance_token_revoked",
) -> Optional[Dict[str, Any]]:
    """
    Revokes one Tower pass.

    Baby version:
    This snatches the pass back.
    """

    data = _load_raw()
    updated = None

    for token in data.get("tokens", []):
        if token.get("token_id") == token_id:
            token["status"] = "revoked"
            token["revoked_at"] = _now()
            token["revoked_by"] = revoked_by
            token["revoke_reason"] = reason
            updated = token
            break

    _save_raw(data)

    if updated:
        write_audit_event(
            actor_user_id=revoked_by,
            target_user_id=updated.get("user_id"),
            action="revoke_clearance_token",
            app_name="tower_admin",
            object_type="clearance_token",
            object_id=token_id,
            result="allow",
            reason_code=reason,
            human_reason="Tower clearance token was revoked.",
            risk_score=70,
            risk_state="restricted",
            metadata={
                "token_id": token_id,
                "scope": updated.get("scope"),
                "app_name": updated.get("app_name"),
                "mode_name": updated.get("mode_name"),
            },
        )

    return updated


def revoke_user_clearance_tokens(
    user_id: str,
    revoked_by: str,
    reason: str = "user_clearance_tokens_revoked",
) -> List[Dict[str, Any]]:
    """
    Revokes all active passes for one user.
    """

    data = _load_raw()
    revoked = []

    for token in data.get("tokens", []):
        if token.get("user_id") == user_id and token.get("status") == "active":
            token["status"] = "revoked"
            token["revoked_at"] = _now()
            token["revoked_by"] = revoked_by
            token["revoke_reason"] = reason
            revoked.append(token)

    _save_raw(data)

    write_audit_event(
        actor_user_id=revoked_by,
        target_user_id=user_id,
        action="revoke_user_clearance_tokens",
        app_name="tower_admin",
        object_type="clearance_token",
        object_id=user_id,
        result="allow",
        reason_code=reason,
        human_reason="All active Tower clearance tokens for user were revoked.",
        risk_score=80,
        risk_state="restricted",
        metadata={
            "user_id": user_id,
            "revoked_count": len(revoked),
        },
    )

    return revoked


def list_clearance_tokens(limit: int = 50) -> List[Dict[str, Any]]:
    data = _load_raw()
    tokens = data.get("tokens", [])
    return tokens[-limit:]
