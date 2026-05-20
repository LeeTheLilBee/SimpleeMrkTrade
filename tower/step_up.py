# =============================================================================
# THE TOWER — STEP-UP AUTHORIZATION
# FILE: tower/step_up.py
# =============================================================================

import json
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from tower.audit import write_audit_event


PROJECT_ROOT = os.environ.get("SIMPLEE_PROJECT_ROOT", "/content/SimpleeMrkTrade_REAL_CLONE")
TOWER_DATA_DIR = Path(PROJECT_ROOT) / "tower" / "data"
STEP_UP_PATH = TOWER_DATA_DIR / "step_up_challenges.json"

TOWER_DATA_DIR.mkdir(parents=True, exist_ok=True)


STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_DENIED = "denied"
STATUS_EXPIRED = "expired"
STATUS_USED = "used"
STATUS_REVOKED = "revoked"


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _parse_time(value: Any) -> Optional[datetime]:
    if not value:
        return None

    try:
        return datetime.fromisoformat(str(value).replace("Z", ""))
    except Exception:
        return None


def _load_raw() -> Dict[str, Any]:
    if not STEP_UP_PATH.exists():
        return {"challenges": []}

    try:
        with STEP_UP_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return {"challenges": []}

        if not isinstance(data.get("challenges"), list):
            data["challenges"] = []

        return data
    except Exception:
        return {"challenges": []}


def _save_raw(data: Dict[str, Any]) -> None:
    tmp_path = STEP_UP_PATH.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True, default=str)

    tmp_path.replace(STEP_UP_PATH)


def create_step_up_challenge(
    user_id: str,
    app_name: str,
    action: str,
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    reason_code: str = "step_up_required",
    expires_minutes: int = 10,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Creates a step-up challenge.

    Baby version:
    The Tower says, "Prove yourself before this dangerous action."
    """

    challenge_id = secrets.token_urlsafe(18)
    created_at = _now()
    expires_at = (datetime.utcnow() + timedelta(minutes=expires_minutes)).isoformat() + "Z"

    challenge = {
        "challenge_id": challenge_id,
        "user_id": user_id,
        "app_name": app_name,
        "action": action,
        "mode_name": mode_name,
        "object_type": object_type,
        "object_id": object_id,
        "reason_code": reason_code,
        "status": STATUS_PENDING,
        "created_at": created_at,
        "expires_at": expires_at,
        "metadata": metadata or {},
        "one_time_use": True,
        "used_at": None,
        "used_by": None,
        "use_reason": None,
    }

    data = _load_raw()
    data["challenges"].append(challenge)
    _save_raw(data)

    write_audit_event(
        actor_user_id=user_id,
        target_user_id=user_id,
        action="create_step_up_challenge",
        app_name=app_name,
        object_type=object_type or "step_up_challenge",
        object_id=object_id or challenge_id,
        result="allow",
        reason_code=reason_code,
        human_reason="Tower step-up challenge was created.",
        risk_score=65,
        risk_state="step_up_required",
        metadata={
            "challenge_id": challenge_id,
            "action": action,
            "mode_name": mode_name,
            "object_type": object_type,
            "object_id": object_id,
        },
    )

    return challenge


def approve_step_up_challenge(
    challenge_id: str,
    approved_by: str,
    approval_note: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Approves a step-up challenge.

    Baby version:
    Owner/admin says, "Yes, this proof is accepted."
    """

    data = _load_raw()
    updated = None

    for challenge in data.get("challenges", []):
        if challenge.get("challenge_id") == challenge_id:
            expires_at = _parse_time(challenge.get("expires_at"))
            if expires_at and expires_at < datetime.utcnow():
                challenge["status"] = STATUS_EXPIRED
                challenge["expired_at"] = _now()
                updated = challenge
                break

            challenge["status"] = STATUS_APPROVED
            challenge["approved_at"] = _now()
            challenge["approved_by"] = approved_by
            if approval_note:
                challenge["approval_note"] = approval_note

            # Keep one-time-use fields present for old compatibility.
            challenge.setdefault("one_time_use", True)
            challenge.setdefault("used_at", None)
            challenge.setdefault("used_by", None)
            challenge.setdefault("use_reason", None)

            updated = challenge
            break

    _save_raw(data)

    if updated:
        write_audit_event(
            actor_user_id=approved_by,
            target_user_id=updated.get("user_id"),
            action="approve_step_up_challenge",
            app_name=updated.get("app_name"),
            object_type=updated.get("object_type") or "step_up_challenge",
            object_id=updated.get("object_id") or challenge_id,
            result="allow",
            reason_code=updated.get("reason_code", "step_up_approved"),
            human_reason="Tower step-up challenge was approved.",
            risk_score=60,
            risk_state="step_up_required",
            metadata={
                "challenge_id": challenge_id,
                "approved_by": approved_by,
            },
        )

    return updated


def deny_step_up_challenge(
    challenge_id: str,
    denied_by: str,
    denial_reason: str = "step_up_denied",
) -> Optional[Dict[str, Any]]:
    data = _load_raw()
    updated = None

    for challenge in data.get("challenges", []):
        if challenge.get("challenge_id") == challenge_id:
            challenge["status"] = STATUS_DENIED
            challenge["denied_at"] = _now()
            challenge["denied_by"] = denied_by
            challenge["denial_reason"] = denial_reason
            updated = challenge
            break

    _save_raw(data)

    if updated:
        write_audit_event(
            actor_user_id=denied_by,
            target_user_id=updated.get("user_id"),
            action="deny_step_up_challenge",
            app_name=updated.get("app_name"),
            object_type=updated.get("object_type") or "step_up_challenge",
            object_id=updated.get("object_id") or challenge_id,
            result="deny",
            reason_code=denial_reason,
            human_reason="Tower step-up challenge was denied.",
            risk_score=75,
            risk_state="restricted",
            metadata={
                "challenge_id": challenge_id,
                "denied_by": denied_by,
            },
        )

    return updated


def revoke_step_up_challenge(
    challenge_id: str,
    revoked_by: str,
    revoke_reason: str = "step_up_revoked",
) -> Optional[Dict[str, Any]]:
    data = _load_raw()
    updated = None

    for challenge in data.get("challenges", []):
        if challenge.get("challenge_id") == challenge_id:
            challenge["status"] = STATUS_REVOKED
            challenge["revoked_at"] = _now()
            challenge["revoked_by"] = revoked_by
            challenge["revoke_reason"] = revoke_reason
            updated = challenge
            break

    _save_raw(data)

    if updated:
        write_audit_event(
            actor_user_id=revoked_by,
            target_user_id=updated.get("user_id"),
            action="revoke_step_up_challenge",
            app_name=updated.get("app_name"),
            object_type=updated.get("object_type") or "step_up_challenge",
            object_id=updated.get("object_id") or challenge_id,
            result="allow",
            reason_code=revoke_reason,
            human_reason="Tower step-up challenge was revoked.",
            risk_score=70,
            risk_state="restricted",
            metadata={
                "challenge_id": challenge_id,
                "revoked_by": revoked_by,
            },
        )

    return updated


def _challenge_matches(
    challenge: Dict[str, Any],
    user_id: str,
    app_name: str,
    action: str,
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    reason_code: Optional[str] = None,
) -> bool:
    if challenge.get("user_id") != user_id:
        return False

    if challenge.get("app_name") != app_name:
        return False

    if challenge.get("action") != action:
        return False

    if mode_name is not None and challenge.get("mode_name") != mode_name:
        return False

    if object_type is not None and challenge.get("object_type") != object_type:
        return False

    if object_id is not None and challenge.get("object_id") != object_id:
        return False

    if reason_code is not None and challenge.get("reason_code") != reason_code:
        return False

    return True


def get_latest_approved_step_up(
    user_id: str,
    app_name: str,
    action: str,
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    reason_code: Optional[str] = None,
    include_used: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Finds the latest approved unused step-up.

    Baby version:
    The Tower looks for an approved ticket that has not been used yet.
    """

    data = _load_raw()
    now = datetime.utcnow()
    matches: List[Dict[str, Any]] = []
    changed = False

    for challenge in data.get("challenges", []):
        # Normalize older records.
        challenge.setdefault("one_time_use", True)
        challenge.setdefault("used_at", None)
        challenge.setdefault("used_by", None)
        challenge.setdefault("use_reason", None)

        if not _challenge_matches(
            challenge=challenge,
            user_id=user_id,
            app_name=app_name,
            action=action,
            mode_name=mode_name,
            object_type=object_type,
            object_id=object_id,
            reason_code=reason_code,
        ):
            continue

        if challenge.get("status") != STATUS_APPROVED:
            continue

        if challenge.get("used_at") and not include_used:
            continue

        expires_at = _parse_time(challenge.get("expires_at"))
        if expires_at and expires_at < now:
            challenge["status"] = STATUS_EXPIRED
            challenge["expired_at"] = _now()
            changed = True
            continue

        matches.append(challenge)

    if changed:
        _save_raw(data)

    if not matches:
        return None

    matches.sort(key=lambda item: item.get("approved_at") or item.get("created_at") or "", reverse=True)
    return matches[0]


def consume_step_up_challenge(
    challenge_id: str,
    used_by: str,
    use_reason: str = "step_up_consumed",
) -> Optional[Dict[str, Any]]:
    """
    Marks a step-up as used.

    Baby version:
    The Tower punches the ticket so it cannot be used again.
    """

    data = _load_raw()
    updated = None

    for challenge in data.get("challenges", []):
        if challenge.get("challenge_id") == challenge_id:
            if challenge.get("status") != STATUS_APPROVED:
                updated = challenge
                break

            challenge["status"] = STATUS_USED
            challenge["used_at"] = _now()
            challenge["used_by"] = used_by
            challenge["use_reason"] = use_reason
            updated = challenge
            break

    _save_raw(data)

    if updated:
        write_audit_event(
            actor_user_id=used_by,
            target_user_id=updated.get("user_id"),
            action="consume_step_up_challenge",
            app_name=updated.get("app_name"),
            object_type=updated.get("object_type") or "step_up_challenge",
            object_id=updated.get("object_id") or challenge_id,
            result="allow",
            reason_code=use_reason,
            human_reason="Tower step-up challenge was consumed.",
            risk_score=55,
            risk_state="step_up_consumed",
            metadata={
                "challenge_id": challenge_id,
                "used_by": used_by,
                "use_reason": use_reason,
            },
        )

    return updated


def consume_latest_approved_step_up(
    user_id: str,
    app_name: str,
    action: str,
    used_by: str,
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    reason_code: Optional[str] = None,
    use_reason: str = "step_up_consumed",
) -> Optional[Dict[str, Any]]:
    challenge = get_latest_approved_step_up(
        user_id=user_id,
        app_name=app_name,
        action=action,
        mode_name=mode_name,
        object_type=object_type,
        object_id=object_id,
        reason_code=reason_code,
    )

    if not challenge:
        return None

    return consume_step_up_challenge(
        challenge_id=challenge.get("challenge_id"),
        used_by=used_by,
        use_reason=use_reason,
    )


def list_step_up_challenges(limit: int = 25) -> List[Dict[str, Any]]:
    data = _load_raw()
    return data.get("challenges", [])[-limit:]


def cleanup_step_up_challenges() -> Dict[str, Any]:
    """
    Marks expired pending/approved challenges as expired.

    Baby version:
    The Tower sweeps old tickets off the desk.
    """

    data = _load_raw()
    now = datetime.utcnow()

    expired = 0
    total = 0

    for challenge in data.get("challenges", []):
        total += 1
        expires_at = _parse_time(challenge.get("expires_at"))

        if not expires_at:
            continue

        if expires_at < now and challenge.get("status") in {STATUS_PENDING, STATUS_APPROVED}:
            challenge["status"] = STATUS_EXPIRED
            challenge["expired_at"] = _now()
            expired += 1

    _save_raw(data)

    return {
        "total_challenges": total,
        "expired_marked": expired,
        "status": "complete",
    }


def get_step_up_summary() -> Dict[str, Any]:
    data = _load_raw()
    rows = data.get("challenges", [])

    summary = {
        "total_step_up_challenges": len(rows),
        "pending": 0,
        "approved": 0,
        "denied": 0,
        "expired": 0,
        "used": 0,
        "revoked": 0,
        "by_app": {},
        "by_action": {},
        "by_reason_code": {},
    }

    for row in rows:
        status = row.get("status") or "unknown"
        app = row.get("app_name") or "unknown"
        action = row.get("action") or "unknown"
        reason = row.get("reason_code") or "unknown"

        if status in summary:
            summary[status] += 1

        summary["by_app"][app] = summary["by_app"].get(app, 0) + 1
        summary["by_action"][action] = summary["by_action"].get(action, 0) + 1
        summary["by_reason_code"][reason] = summary["by_reason_code"].get(reason, 0) + 1

    return summary
