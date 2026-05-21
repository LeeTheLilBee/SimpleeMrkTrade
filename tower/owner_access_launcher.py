
"""
The Tower — Owner Access Launcher

This is a notebook/dev helper for owner-only Tower access.

It does NOT create a master key.
It issues separate short-lived keycards for separate Tower doors.

Use:
    from tower.owner_access_launcher import create_owner_tower_launch
    launch = create_owner_tower_launch()
    print(launch["urls"]["command"])
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict

from tower.keycard_issuer import issue_owner_tower_access_urls


DEFAULT_SESSION_ID = "session_owner_launcher"
DEFAULT_DEVICE_ID = "device_owner_primary"
DEFAULT_TTL_SECONDS = 20 * 60


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def create_owner_tower_launch(
    *,
    actor_user_id: str = "owner_solice",
    target_user_id: str = "owner_solice",
    session_id: str = DEFAULT_SESSION_ID,
    device_id: str = DEFAULT_DEVICE_ID,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    include_regenerate: bool = False,
    base_url: str = "",
    reason: str = "Owner launched The Tower from notebook helper.",
) -> Dict[str, Any]:
    """
    Create temporary Tower access URLs.

    Returns URLs for:
    - entry
    - command
    - status
    - regenerate, only if requested

    Each URL carries a different keycard pass scoped to its door.
    """
    payload = issue_owner_tower_access_urls(
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
        reason=reason,
        ttl_seconds=ttl_seconds,
        session_id=session_id,
        device_id=device_id,
        include_regenerate=include_regenerate,
        base_url=base_url,
    )

    if not payload.get("ok"):
        return payload

    return {
        "ok": True,
        "status": "issued",
        "tower_name": "The Tower",
        "human_reason": "Temporary owner Tower launch URLs issued. Each door has its own scoped keycard.",
        "issued_at": _utc_now(),
        "expires_in_seconds": ttl_seconds,
        "actor_user_id": actor_user_id,
        "target_user_id": target_user_id,
        "session_id": session_id,
        "device_id": device_id,
        "urls": payload.get("urls", {}),
        "issued_keys": sorted(payload.get("issued", {}).keys()),
        "safety_note": "Do not paste these URLs into public chats. They contain temporary scoped keycard tokens.",
    }


def print_owner_tower_launch(**kwargs) -> Dict[str, Any]:
    """
    Print a readable launch packet for notebook use.
    """
    launch = create_owner_tower_launch(**kwargs)

    print("=" * 80)
    print("THE TOWER OWNER ACCESS LAUNCH")
    print("=" * 80)

    if not launch.get("ok"):
        print(json.dumps(launch, indent=2, sort_keys=True))
        return launch

    print("Status:", launch.get("status"))
    print("Expires in seconds:", launch.get("expires_in_seconds"))
    print("Session:", launch.get("session_id"))
    print("Device:", launch.get("device_id"))
    print()
    print("Open these in your Flask/Colab forwarded app:")
    print()

    urls = launch.get("urls", {})
    for key in ["entry", "command", "status", "regenerate"]:
        if key in urls:
            print(f"{key.upper()}:")
            print(urls[key])
            print()

    print("Safety note:")
    print(launch.get("safety_note"))
    return launch


if __name__ == "__main__":
    print_owner_tower_launch()
