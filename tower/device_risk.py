# =============================================================================
# THE TOWER — DEVICE + SESSION RISK
# FILE: tower/device_risk.py
# =============================================================================

import hashlib
import json
import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from tower.audit import write_audit_event
from tower.security_events import create_security_event


PROJECT_ROOT = os.environ.get("SIMPLEE_PROJECT_ROOT", "/content/SimpleeMrkTrade_REAL_CLONE")
TOWER_DATA_DIR = Path(PROJECT_ROOT) / "tower" / "data"
DEVICES_PATH = TOWER_DATA_DIR / "devices.json"
SESSIONS_PATH = TOWER_DATA_DIR / "sessions.json"

TOWER_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _hash_text(value: str) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()


def _load_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return default

        return data
    except Exception:
        return default


def _save_json(path: Path, data: Dict[str, Any]) -> None:
    tmp_path = path.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True, default=str)

    tmp_path.replace(path)


def _load_devices() -> Dict[str, Any]:
    data = _load_json(DEVICES_PATH, {"devices": []})
    if not isinstance(data.get("devices"), list):
        data["devices"] = []
    return data


def _save_devices(data: Dict[str, Any]) -> None:
    _save_json(DEVICES_PATH, data)


def _load_sessions() -> Dict[str, Any]:
    data = _load_json(SESSIONS_PATH, {"sessions": []})
    if not isinstance(data.get("sessions"), list):
        data["sessions"] = []
    return data


def _save_sessions(data: Dict[str, Any]) -> None:
    _save_json(SESSIONS_PATH, data)


def make_device_fingerprint(
    user_agent: str = "",
    ip_address: str = "",
    device_hint: str = "",
) -> str:
    """
    Makes a stable-ish device fingerprint.

    Baby version:
    This is the device name tag.
    """

    raw = "|".join([
        str(user_agent or "").strip().lower(),
        str(ip_address or "").strip(),
        str(device_hint or "").strip().lower(),
    ])
    return _hash_text(raw)


def get_device(user_id: str, device_fingerprint: str) -> Optional[Dict[str, Any]]:
    data = _load_devices()

    for device in data.get("devices", []):
        if device.get("user_id") == user_id and device.get("device_fingerprint") == device_fingerprint:
            return device

    return None


def register_or_update_device(
    user_id: str,
    user_agent: str = "",
    ip_address: str = "",
    device_hint: str = "",
    trusted: bool = False,
    actor_user_id: str = "tower",
) -> Dict[str, Any]:
    """
    Registers or updates a known device.

    Baby version:
    This says, "I saw this device before" or "This is a new device."
    """

    data = _load_devices()
    fingerprint = make_device_fingerprint(
        user_agent=user_agent,
        ip_address=ip_address,
        device_hint=device_hint,
    )

    existing = None
    for device in data.get("devices", []):
        if device.get("user_id") == user_id and device.get("device_fingerprint") == fingerprint:
            existing = device
            break

    now = _now()

    if existing:
        existing["last_seen_at"] = now
        existing["seen_count"] = int(existing.get("seen_count") or 0) + 1
        existing["last_ip_hash"] = _hash_text(ip_address)
        existing["last_user_agent_hash"] = _hash_text(user_agent)
        existing["device_hint"] = device_hint
        existing["trusted"] = bool(existing.get("trusted") or trusted)
        device = existing
        created_new = False
    else:
        device = {
            "device_id": secrets.token_urlsafe(12),
            "user_id": user_id,
            "device_fingerprint": fingerprint,
            "device_hint": device_hint,
            "trusted": bool(trusted),
            "first_seen_at": now,
            "last_seen_at": now,
            "seen_count": 1,
            "last_ip_hash": _hash_text(ip_address),
            "last_user_agent_hash": _hash_text(user_agent),
            "status": "active",
        }
        data["devices"].append(device)
        created_new = True

    _save_devices(data)

    write_audit_event(
        actor_user_id=actor_user_id,
        target_user_id=user_id,
        action="register_or_update_device",
        app_name="tower_admin",
        object_type="device",
        object_id=device.get("device_id"),
        result="allow",
        reason_code="device_registered_or_updated",
        human_reason="Tower device record was registered or updated.",
        risk_score=45 if created_new else 15,
        risk_state="watch" if created_new else "clear",
        metadata={
            "created_new": created_new,
            "device_id": device.get("device_id"),
            "trusted": device.get("trusted"),
            "device_hint": device_hint,
        },
    )

    if created_new:
        create_security_event(
            user_id=user_id,
            event_type="new_device_seen",
            severity="medium",
            source_app="tower_admin",
            description="A new device was seen for this user.",
            recommended_action="verify_device_if_sensitive_actions_are_requested",
            metadata={
                "device_id": device.get("device_id"),
                "device_hint": device_hint,
            },
        )

    return device


def create_session(
    user_id: str,
    user_agent: str = "",
    ip_address: str = "",
    device_hint: str = "",
    app_name: str = "tower",
    actor_user_id: str = "tower",
) -> Dict[str, Any]:
    """
    Creates a session and calculates basic risk.

    Baby version:
    This starts a visit and checks whether it feels normal or funny.
    """

    device = register_or_update_device(
        user_id=user_id,
        user_agent=user_agent,
        ip_address=ip_address,
        device_hint=device_hint,
        trusted=False,
        actor_user_id=actor_user_id,
    )

    risk = evaluate_session_risk(
        user_id=user_id,
        device_id=device.get("device_id"),
        device_trusted=bool(device.get("trusted")),
        new_device=int(device.get("seen_count") or 0) <= 1,
        failed_attempts=0,
    )

    session = {
        "session_id": secrets.token_urlsafe(18),
        "user_id": user_id,
        "app_name": app_name,
        "device_id": device.get("device_id"),
        "device_fingerprint": device.get("device_fingerprint"),
        "created_at": _now(),
        "last_seen_at": _now(),
        "status": "active",
        "risk_score": risk.get("risk_score"),
        "risk_state": risk.get("risk_state"),
        "risk_reasons": risk.get("risk_reasons"),
        "failed_attempts": 0,
        "ip_hash": _hash_text(ip_address),
        "user_agent_hash": _hash_text(user_agent),
    }

    data = _load_sessions()
    data["sessions"].append(session)
    _save_sessions(data)

    write_audit_event(
        actor_user_id=actor_user_id,
        target_user_id=user_id,
        action="create_session",
        app_name=app_name,
        object_type="session",
        object_id=session.get("session_id"),
        result="allow",
        reason_code="session_created",
        human_reason="Tower session was created.",
        risk_score=int(session.get("risk_score") or 0),
        risk_state=session.get("risk_state") or "clear",
        metadata={
            "session_id": session.get("session_id"),
            "device_id": session.get("device_id"),
            "risk_reasons": session.get("risk_reasons"),
        },
    )

    return session


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    data = _load_sessions()

    for session in data.get("sessions", []):
        if session.get("session_id") == session_id:
            return session

    return None


def update_session_risk(
    session_id: str,
    failed_attempt_delta: int = 0,
    actor_user_id: str = "tower",
) -> Optional[Dict[str, Any]]:
    """
    Updates session risk.

    Baby version:
    If this session keeps failing doors, it gets more suspicious.
    """

    data = _load_sessions()
    updated = None

    for session in data.get("sessions", []):
        if session.get("session_id") != session_id:
            continue

        session["failed_attempts"] = int(session.get("failed_attempts") or 0) + int(failed_attempt_delta or 0)
        session["last_seen_at"] = _now()

        risk = evaluate_session_risk(
            user_id=session.get("user_id"),
            device_id=session.get("device_id"),
            device_trusted=False,
            new_device=False,
            failed_attempts=int(session.get("failed_attempts") or 0),
        )

        session["risk_score"] = risk.get("risk_score")
        session["risk_state"] = risk.get("risk_state")
        session["risk_reasons"] = risk.get("risk_reasons")
        updated = session
        break

    _save_sessions(data)

    if updated:
        write_audit_event(
            actor_user_id=actor_user_id,
            target_user_id=updated.get("user_id"),
            action="update_session_risk",
            app_name=updated.get("app_name"),
            object_type="session",
            object_id=session_id,
            result="allow",
            reason_code="session_risk_updated",
            human_reason="Tower session risk was updated.",
            risk_score=int(updated.get("risk_score") or 0),
            risk_state=updated.get("risk_state") or "clear",
            metadata={
                "session_id": session_id,
                "failed_attempts": updated.get("failed_attempts"),
                "risk_reasons": updated.get("risk_reasons"),
            },
        )

        if int(updated.get("risk_score") or 0) >= 70:
            create_security_event(
                user_id=updated.get("user_id"),
                event_type="session_risk_high",
                severity="high" if int(updated.get("risk_score") or 0) < 90 else "critical",
                source_app=updated.get("app_name"),
                description="A session risk score became high.",
                recommended_action="require_step_up_or_quarantine_session",
                metadata={
                    "session_id": session_id,
                    "risk_score": updated.get("risk_score"),
                    "risk_state": updated.get("risk_state"),
                    "risk_reasons": updated.get("risk_reasons"),
                },
            )

    return updated


def revoke_session(
    session_id: str,
    revoked_by: str,
    reason: str = "session_revoked",
) -> Optional[Dict[str, Any]]:
    """
    Revokes a session.

    Baby version:
    This kicks the visit out.
    """

    data = _load_sessions()
    updated = None

    for session in data.get("sessions", []):
        if session.get("session_id") == session_id:
            session["status"] = "revoked"
            session["revoked_at"] = _now()
            session["revoked_by"] = revoked_by
            session["revoke_reason"] = reason
            updated = session
            break

    _save_sessions(data)

    if updated:
        write_audit_event(
            actor_user_id=revoked_by,
            target_user_id=updated.get("user_id"),
            action="revoke_session",
            app_name=updated.get("app_name"),
            object_type="session",
            object_id=session_id,
            result="allow",
            reason_code=reason,
            human_reason="Tower session was revoked.",
            risk_score=80,
            risk_state="restricted",
            metadata={
                "session_id": session_id,
            },
        )

    return updated


def evaluate_session_risk(
    user_id: str,
    device_id: Optional[str] = None,
    device_trusted: bool = False,
    new_device: bool = False,
    failed_attempts: int = 0,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Calculates a simple risk score.

    Baby version:
    More weird stuff = higher score.
    """

    context = context or {}

    score = 0
    reasons = []

    if new_device:
        score += 35
        reasons.append("new_device")

    if not device_trusted:
        score += 10
        reasons.append("device_not_trusted")

    if failed_attempts >= 1:
        # Failed attempts should get serious quickly.
        # Baby version:
        # One or two mistakes = watch.
        # A bunch of mistakes = step-up.
        # Way too many mistakes = quarantine.
        score += min(60, failed_attempts * 12)
        reasons.append("failed_attempts")

        if failed_attempts >= 5:
            score += 15
            reasons.append("many_failed_attempts")

        if failed_attempts >= 10:
            score += 25
            reasons.append("excessive_failed_attempts")

    if context.get("sensitive_action"):
        score += 20
        reasons.append("sensitive_action")

    if context.get("new_location_hint"):
        score += 20
        reasons.append("new_location_hint")

    if context.get("rapid_denials"):
        score += 25
        reasons.append("rapid_denials")

    if score >= 90:
        state = "quarantine_recommended"
    elif score >= 70:
        state = "step_up_required"
    elif score >= 40:
        state = "watch"
    else:
        state = "clear"

    return {
        "user_id": user_id,
        "device_id": device_id,
        "risk_score": score,
        "risk_state": state,
        "risk_reasons": reasons,
    }


def list_sessions(limit: int = 50) -> List[Dict[str, Any]]:
    data = _load_sessions()
    return data.get("sessions", [])[-limit:]


def list_devices(limit: int = 50) -> List[Dict[str, Any]]:
    data = _load_devices()
    return data.get("devices", [])[-limit:]
