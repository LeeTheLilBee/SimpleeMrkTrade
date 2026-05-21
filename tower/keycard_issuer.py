
"""
The Tower — Owner Keycard Issuer

This module creates short-lived scoped keycard passes for Tower doors.

Important:
- This is NOT a public login system.
- This is an owner/admin issuance layer.
- Every pass is still scoped to one exact door.
- A pass for /tower does not open /tower/status.json.
- A pass for /tower/security-command does not open regenerate.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from tower.keycard_passes import issue_keycard_pass


OWNER_USER_IDS = {"owner_solice"}
ADMIN_USER_IDS = set()

DEFAULT_TOWER_SESSION_ID = "session_owner_tower"
DEFAULT_TOWER_DEVICE_ID = "device_owner_primary"
DEFAULT_TTL_SECONDS = 20 * 60

TOWER_DOORS = {
    "entry": {
        "door_id": "/tower",
        "actions": ["view"],
        "clearance_level": "restricted",
        "label": "Tower Entry",
    },
    "command": {
        "door_id": "/tower/security-command",
        "actions": ["view"],
        "clearance_level": "restricted",
        "label": "Security Command",
    },
    "status": {
        "door_id": "/tower/status.json",
        "actions": ["view"],
        "clearance_level": "restricted",
        "label": "Tower Status JSON",
    },
    "regenerate": {
        "door_id": "/tower/security-command/regenerate",
        "actions": ["regenerate"],
        "clearance_level": "critical",
        "label": "Regenerate Security Command",
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _is_owner(actor_user_id: str) -> bool:
    return _safe_str(actor_user_id) in OWNER_USER_IDS


def _is_admin(actor_user_id: str) -> bool:
    return _safe_str(actor_user_id) in ADMIN_USER_IDS


def _actor_can_issue(actor_user_id: str, *, allow_admin: bool = False) -> bool:
    actor_user_id = _safe_str(actor_user_id)
    if _is_owner(actor_user_id):
        return True
    if allow_admin and _is_admin(actor_user_id):
        return True
    return False


def _deny(reason_code: str, human_reason: str, **metadata) -> Dict[str, Any]:
    return {
        "ok": False,
        "allowed": False,
        "decision": "deny",
        "reason_code": reason_code,
        "human_reason": human_reason,
        "metadata": dict(metadata or {}),
        "issued_at": _utc_now(),
    }


def get_tower_door_catalog() -> Dict[str, Any]:
    return {
        "ok": True,
        "tower_name": "The Tower",
        "doors": copy.deepcopy(TOWER_DOORS),
        "human_reason": "Tower keycard door catalog loaded.",
    }


def issue_tower_route_keycard(
    *,
    actor_user_id: str,
    target_user_id: str,
    door_key: str,
    reason: str,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    session_id: str = DEFAULT_TOWER_SESSION_ID,
    device_id: str = DEFAULT_TOWER_DEVICE_ID,
    allow_admin: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Issue one scoped Tower route keycard.

    actor_user_id:
        Who is requesting/issuing the pass.

    target_user_id:
        Who the pass belongs to.

    door_key:
        entry, command, status, regenerate

    reason:
        Required. Goes into the keycard issue record.
    """
    actor_user_id = _safe_str(actor_user_id)
    target_user_id = _safe_str(target_user_id)
    door_key = _safe_str(door_key)
    reason = _safe_str(reason)

    if not _actor_can_issue(actor_user_id, allow_admin=allow_admin):
        return _deny(
            "owner_keycard_issuer_required",
            "Only the owner can issue Tower keycard passes right now.",
            actor_user_id=actor_user_id,
            target_user_id=target_user_id,
            door_key=door_key,
        )

    if not target_user_id:
        return _deny(
            "target_user_required",
            "A target user is required before issuing a Tower keycard pass.",
            actor_user_id=actor_user_id,
            door_key=door_key,
        )

    if door_key not in TOWER_DOORS:
        return _deny(
            "unknown_tower_door",
            "That Tower door is not in the keycard catalog.",
            actor_user_id=actor_user_id,
            target_user_id=target_user_id,
            door_key=door_key,
        )

    if not reason:
        return _deny(
            "issue_reason_required",
            "A reason is required to issue a Tower keycard pass.",
            actor_user_id=actor_user_id,
            target_user_id=target_user_id,
            door_key=door_key,
        )

    door = TOWER_DOORS[door_key]
    result = issue_keycard_pass(
        user_id=target_user_id,
        app_name="tower",
        door_type="route",
        door_id=door["door_id"],
        actions=door["actions"],
        issuer_user_id=actor_user_id,
        reason=reason,
        ttl_seconds=int(ttl_seconds or DEFAULT_TTL_SECONDS),
        session_id=session_id,
        device_id=device_id,
        role="owner" if target_user_id in OWNER_USER_IDS else "user",
        clearance_level=door["clearance_level"],
        risk_score_at_issue=0,
        metadata={
            "source": "tower_keycard_issuer",
            "door_key": door_key,
            "door_label": door["label"],
            **dict(metadata or {}),
        },
    )

    return {
        "ok": True,
        "allowed": True,
        "decision": "allow",
        "status": "issued",
        "reason_code": "tower_keycard_issued",
        "human_reason": f"Tower keycard issued for {door['label']}.",
        "door_key": door_key,
        "door": copy.deepcopy(door),
        "target_user_id": target_user_id,
        "actor_user_id": actor_user_id,
        "session_id": session_id,
        "device_id": device_id,
        "expires_at": result.get("expires_at"),
        "pass_id": result.get("pass_id"),
        "token": result.get("token"),
        "token_preview": result.get("token_preview"),
    }


def issue_owner_tower_keycard_bundle(
    *,
    actor_user_id: str = "owner_solice",
    target_user_id: str = "owner_solice",
    reason: str = "Owner Tower command access bundle.",
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    session_id: str = DEFAULT_TOWER_SESSION_ID,
    device_id: str = DEFAULT_TOWER_DEVICE_ID,
    include_regenerate: bool = False,
) -> Dict[str, Any]:
    """
    Issue a bundle of separate passes.

    Important:
        This does not create one master pass.
        It creates separate passes per door.
    """
    actor_user_id = _safe_str(actor_user_id)
    target_user_id = _safe_str(target_user_id)

    if not _actor_can_issue(actor_user_id):
        return _deny(
            "owner_keycard_issuer_required",
            "Only the owner can issue the Tower keycard bundle.",
            actor_user_id=actor_user_id,
            target_user_id=target_user_id,
        )

    door_keys = ["entry", "command", "status"]
    if include_regenerate:
        door_keys.append("regenerate")

    issued = {}
    failures = {}

    for door_key in door_keys:
        result = issue_tower_route_keycard(
            actor_user_id=actor_user_id,
            target_user_id=target_user_id,
            door_key=door_key,
            reason=f"{reason} Door: {door_key}.",
            ttl_seconds=ttl_seconds,
            session_id=session_id,
            device_id=device_id,
            metadata={"bundle": True, "include_regenerate": include_regenerate},
        )
        if result.get("ok"):
            issued[door_key] = result
        else:
            failures[door_key] = result

    return {
        "ok": not failures,
        "allowed": not failures,
        "decision": "allow" if not failures else "partial",
        "status": "issued" if not failures else "partial",
        "reason_code": "tower_keycard_bundle_issued" if not failures else "tower_keycard_bundle_partial",
        "human_reason": "Tower keycard bundle issued." if not failures else "Some Tower keycards could not be issued.",
        "actor_user_id": actor_user_id,
        "target_user_id": target_user_id,
        "session_id": session_id,
        "device_id": device_id,
        "ttl_seconds": ttl_seconds,
        "issued": issued,
        "failures": failures,
    }


def build_tower_open_urls(
    *,
    bundle: Dict[str, Any],
    base_url: str = "",
) -> Dict[str, Any]:
    """
    Build local URLs with the correct keycard per door.
    For notebook/dev convenience only.
    """
    issued = bundle.get("issued", {}) if isinstance(bundle, dict) else {}

    urls = {}
    for door_key, item in issued.items():
        door = item.get("door", {})
        door_id = door.get("door_id")
        token = item.get("token")
        target_user_id = item.get("target_user_id")
        session_id = item.get("session_id")
        device_id = item.get("device_id")

        if not door_id or not token:
            continue

        query = (
            f"tower_user_id={target_user_id}"
            f"&tower_keycard={token}"
            f"&tower_session_id={session_id}"
            f"&tower_device_id={device_id}"
        )
        urls[door_key] = f"{base_url}{door_id}?{query}"

    return {
        "ok": True,
        "urls": urls,
        "human_reason": "Tower open URLs built from scoped keycard passes.",
    }


def issue_owner_tower_access_urls(
    *,
    actor_user_id: str = "owner_solice",
    target_user_id: str = "owner_solice",
    reason: str = "Owner Tower access URL request.",
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    session_id: str = DEFAULT_TOWER_SESSION_ID,
    device_id: str = DEFAULT_TOWER_DEVICE_ID,
    include_regenerate: bool = False,
    base_url: str = "",
) -> Dict[str, Any]:
    bundle = issue_owner_tower_keycard_bundle(
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
        reason=reason,
        ttl_seconds=ttl_seconds,
        session_id=session_id,
        device_id=device_id,
        include_regenerate=include_regenerate,
    )

    if not bundle.get("ok"):
        return bundle

    url_payload = build_tower_open_urls(bundle=bundle, base_url=base_url)
    return {
        **bundle,
        "urls": url_payload.get("urls", {}),
        "human_reason": "Owner Tower access URLs issued. Each URL carries a different scoped keycard.",
    }
