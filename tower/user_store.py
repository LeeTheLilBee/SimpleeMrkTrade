# =============================================================================
# THE TOWER — USER STORE
# FILE: tower/user_store.py
# =============================================================================

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from tower.audit import write_audit_event


PROJECT_ROOT = os.environ.get("SIMPLEE_PROJECT_ROOT", "/content/SimpleeMrkTrade_REAL_CLONE")
TOWER_DATA_DIR = Path(PROJECT_ROOT) / "tower" / "data"
USERS_PATH = TOWER_DATA_DIR / "tower_users.json"

TOWER_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _load_raw() -> Dict[str, Any]:
    if not USERS_PATH.exists():
        return {"users": []}

    try:
        with USERS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return {"users": []}

        if not isinstance(data.get("users"), list):
            data["users"] = []

        return data
    except Exception:
        return {"users": []}


def _save_raw(data: Dict[str, Any]) -> None:
    TOWER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    tmp_path = USERS_PATH.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True, default=str)

    tmp_path.replace(USERS_PATH)


def list_users() -> List[Dict[str, Any]]:
    """
    Returns every Tower user.

    Baby version:
    This reads the user address book.
    """

    return _load_raw().get("users", [])


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Finds one user by user_id.
    """

    for user in list_users():
        if str(user.get("user_id")) == str(user_id):
            return user

    return None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Finds one user by email.
    """

    email = str(email or "").strip().lower()

    for user in list_users():
        if str(user.get("email", "")).strip().lower() == email:
            return user

    return None


def upsert_user(
    user: Dict[str, Any],
    actor_user_id: str = "system",
    reason: str = "upsert_user",
    write_audit: bool = True,
) -> Dict[str, Any]:
    """
    Creates or updates a Tower user.

    Baby version:
    If the user exists, update them.
    If they do not exist, add them.
    """

    if not user.get("user_id"):
        raise ValueError("user_id is required")

    now = _now()
    data = _load_raw()
    users = data.get("users", [])

    user = dict(user)
    user.setdefault("created_at", now)
    user["updated_at"] = now

    found = False
    new_users = []

    for existing in users:
        if str(existing.get("user_id")) == str(user.get("user_id")):
            merged = dict(existing)
            merged.update(user)
            merged.setdefault("created_at", existing.get("created_at", now))
            merged["updated_at"] = now
            new_users.append(merged)
            found = True
        else:
            new_users.append(existing)

    if not found:
        new_users.append(user)

    data["users"] = new_users
    data["updated_at"] = now
    _save_raw(data)

    if write_audit:
        write_audit_event(
            actor_user_id=actor_user_id,
            target_user_id=str(user.get("user_id")),
            action="upsert_user",
            app_name="tower_admin",
            object_type="tower_user",
            object_id=str(user.get("user_id")),
            result="allow",
            reason_code=reason,
            human_reason="Tower user record was created or updated.",
            risk_score=20,
            risk_state="clear",
            metadata={
                "created_new": not found,
                "email": user.get("email"),
                "role": user.get("role"),
                "account_type": user.get("account_type"),
                "status": user.get("status"),
            },
        )

    return get_user(str(user.get("user_id"))) or user


def update_user_status(
    user_id: str,
    status: str,
    actor_user_id: str = "system",
    reason: str = "status_update",
) -> Optional[Dict[str, Any]]:
    """
    Changes a user's status.

    Example statuses:
    active
    locked
    quarantined
    revoked
    """

    user = get_user(user_id)
    if not user:
        return None

    old_status = user.get("status")
    user["status"] = status

    updated = upsert_user(
        user=user,
        actor_user_id=actor_user_id,
        reason=reason,
        write_audit=False,
    )

    write_audit_event(
        actor_user_id=actor_user_id,
        target_user_id=user_id,
        action="update_user_status",
        app_name="tower_admin",
        object_type="tower_user",
        object_id=user_id,
        result="allow",
        reason_code=reason,
        human_reason=f"Tower user status changed from {old_status} to {status}.",
        risk_score=70 if status in {"locked", "quarantined", "revoked"} else 30,
        risk_state=status if status in {"locked", "quarantined"} else "clear",
        metadata={
            "old_status": old_status,
            "new_status": status,
        },
    )

    return updated


def grant_app_access(
    user_id: str,
    app_name: str,
    actor_user_id: str = "system",
    reason: str = "grant_app_access",
) -> Optional[Dict[str, Any]]:
    """
    Gives a user access to an app.
    """

    user = get_user(user_id)
    if not user:
        return None

    app_access = user.get("app_access", {})
    app_access[app_name] = "allowed"
    user["app_access"] = app_access

    updated = upsert_user(
        user=user,
        actor_user_id=actor_user_id,
        reason=reason,
        write_audit=False,
    )

    write_audit_event(
        actor_user_id=actor_user_id,
        target_user_id=user_id,
        action="grant_app_access",
        app_name="tower_admin",
        object_type="app_access",
        object_id=f"{user_id}:{app_name}",
        result="allow",
        reason_code=reason,
        human_reason=f"App access granted for {app_name}.",
        risk_score=50,
        risk_state="clear",
        metadata={
            "user_id": user_id,
            "app_name": app_name,
        },
    )

    return updated


def revoke_app_access(
    user_id: str,
    app_name: str,
    actor_user_id: str = "system",
    reason: str = "revoke_app_access",
) -> Optional[Dict[str, Any]]:
    """
    Removes a user's access to an app.
    """

    user = get_user(user_id)
    if not user:
        return None

    app_access = user.get("app_access", {})
    app_access[app_name] = "denied"
    user["app_access"] = app_access

    updated = upsert_user(
        user=user,
        actor_user_id=actor_user_id,
        reason=reason,
        write_audit=False,
    )

    write_audit_event(
        actor_user_id=actor_user_id,
        target_user_id=user_id,
        action="revoke_app_access",
        app_name="tower_admin",
        object_type="app_access",
        object_id=f"{user_id}:{app_name}",
        result="allow",
        reason_code=reason,
        human_reason=f"App access revoked for {app_name}.",
        risk_score=60,
        risk_state="restricted",
        metadata={
            "user_id": user_id,
            "app_name": app_name,
        },
    )

    return updated


def set_consent(
    user_id: str,
    consent_key: str,
    accepted: bool,
    actor_user_id: str = "system",
    reason: str = "set_consent",
) -> Optional[Dict[str, Any]]:
    """
    Marks whether a user accepted a consent/disclosure.
    """

    user = get_user(user_id)
    if not user:
        return None

    consents = user.get("consents", {})
    consents[consent_key] = bool(accepted)
    user["consents"] = consents

    updated = upsert_user(
        user=user,
        actor_user_id=actor_user_id,
        reason=reason,
        write_audit=False,
    )

    write_audit_event(
        actor_user_id=actor_user_id,
        target_user_id=user_id,
        action="set_consent",
        app_name="tower_admin",
        object_type="consent",
        object_id=f"{user_id}:{consent_key}",
        result="allow",
        reason_code=reason,
        human_reason=f"Consent {consent_key} was set to {accepted}.",
        risk_score=35,
        risk_state="clear",
        metadata={
            "user_id": user_id,
            "consent_key": consent_key,
            "accepted": accepted,
        },
    )

    return updated
