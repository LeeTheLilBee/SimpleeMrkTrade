# =============================================================================
# THE TOWER — STEP-UP AUTHORIZATION
# FILE: tower/step_up.py
# =============================================================================

import json
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional


PROJECT_ROOT = os.environ.get("SIMPLEE_PROJECT_ROOT", "/content/SimpleeMrkTrade_REAL_CLONE")
TOWER_DATA_DIR = Path(PROJECT_ROOT) / "tower" / "data"
STEP_UP_PATH = TOWER_DATA_DIR / "step_up_challenges.json"

TOWER_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _expires(minutes: int = 10) -> str:
    return (datetime.utcnow() + timedelta(minutes=minutes)).isoformat() + "Z"


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
    minutes_valid: int = 10,
) -> Dict[str, Any]:
    """
    Creates a temporary step-up challenge.

    Baby version:
    This makes a little ticket that says:
    "Prove it's really you before doing the scary thing."
    """

    data = _load_raw()

    challenge = {
        "challenge_id": secrets.token_urlsafe(18),
        "user_id": user_id,
        "app_name": app_name,
        "action": action,
        "mode_name": mode_name,
        "object_type": object_type,
        "object_id": object_id,
        "reason_code": reason_code,
        "status": "pending",
        "created_at": _now(),
        "expires_at": _expires(minutes_valid),
        "approved_at": None,
        "approved_by": None,
    }

    data["challenges"].append(challenge)
    _save_raw(data)
    return challenge


def approve_step_up_challenge(
    challenge_id: str,
    approved_by: str,
) -> Optional[Dict[str, Any]]:
    """
    Approves a pending challenge.

    Baby version:
    This says, "Okay, the extra proof passed."
    """

    data = _load_raw()
    updated = None

    for challenge in data.get("challenges", []):
        if challenge.get("challenge_id") == challenge_id:
            challenge["status"] = "approved"
            challenge["approved_at"] = _now()
            challenge["approved_by"] = approved_by
            updated = challenge
            break

    _save_raw(data)
    return updated


def get_latest_approved_step_up(
    user_id: str,
    app_name: str,
    action: str,
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Finds a valid approved step-up challenge.

    Baby version:
    Checks if the user already proved themselves recently.
    """

    data = _load_raw()
    now = datetime.utcnow()

    matches = []

    for challenge in data.get("challenges", []):
        if challenge.get("status") != "approved":
            continue

        if challenge.get("user_id") != user_id:
            continue

        if challenge.get("app_name") != app_name:
            continue

        if challenge.get("action") != action:
            continue

        if mode_name is not None and challenge.get("mode_name") != mode_name:
            continue

        if object_type is not None and challenge.get("object_type") != object_type:
            continue

        if object_id is not None and challenge.get("object_id") != object_id:
            continue

        try:
            expires_at = datetime.fromisoformat(str(challenge.get("expires_at")).replace("Z", ""))
            if expires_at < now:
                continue
        except Exception:
            continue

        matches.append(challenge)

    if not matches:
        return None

    matches.sort(key=lambda item: item.get("approved_at") or "", reverse=True)
    return matches[0]
