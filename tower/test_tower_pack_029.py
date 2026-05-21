
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

for name in list(sys.modules.keys()):
    if name == "tower" or name.startswith("tower.") or name == "web.app":
        sys.modules.pop(name, None)

from tower.owner_access_launcher import create_owner_tower_launch
from web.app import app


BASE_HTML = PROJECT_ROOT / "web" / "templates" / "base.html"


def _print(title, payload=None):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def run_tests():
    _print("CREATE OWNER LAUNCH")
    launch = create_owner_tower_launch(
        actor_user_id="owner_solice",
        target_user_id="owner_solice",
        session_id="session_pack029",
        device_id="device_pack029",
        ttl_seconds=900,
        include_regenerate=True,
    )
    _print("launch summary", {
        "ok": launch.get("ok"),
        "issued_keys": launch.get("issued_keys"),
        "url_keys": sorted(launch.get("urls", {}).keys()),
        "expires": launch.get("expires_in_seconds"),
    })

    assert launch["ok"] is True
    assert sorted(launch["urls"].keys()) == ["command", "entry", "regenerate", "status"]
    assert "tower_keycard=" in launch["urls"]["command"]
    assert "tower_keycard=" in launch["urls"]["entry"]
    assert "tower_keycard=" in launch["urls"]["status"]

    client = app.test_client()

    _print("UNKEYED BASE TOWER ROUTE LOCKS")
    locked = client.get("/tower")
    locked_text = locked.get_data(as_text=True)
    _print("locked", {"status": locked.status_code, "preview": locked_text[:220]})
    assert locked.status_code == 403
    assert "Clearance required" in locked_text
    assert "Open Security Command" not in locked_text

    _print("KEYED ENTRY OPENS")
    entry = client.get(launch["urls"]["entry"])
    entry_text = entry.get_data(as_text=True)
    _print("entry", {"status": entry.status_code, "preview": entry_text[:260]})
    assert entry.status_code == 200
    assert "The Tower" in entry_text
    assert "Open Security Command" in entry_text

    _print("KEYED COMMAND OPENS")
    command = client.get(launch["urls"]["command"])
    command_text = command.get_data(as_text=True)
    _print("command", {"status": command.status_code, "has_health": "Tower health gauge" in command_text})
    assert command.status_code == 200
    assert "Tower health gauge" in command_text
    assert "Soulaana" in command_text

    _print("KEYED STATUS OPENS")
    status = client.get(launch["urls"]["status"])
    status_json = status.get_json(silent=True)
    _print("status", {"status": status.status_code, "json_ok": bool(status_json and status_json.get("ok"))})
    assert status.status_code == 200
    assert isinstance(status_json, dict)
    assert status_json.get("ok") is True
    assert "security_inbox_total" in status_json

    _print("BASE TEMPLATE LINK IS SAFE")
    base = BASE_HTML.read_text(encoding="utf-8", errors="replace")
    assert 'href="/tower/security-command?tower_user_id=owner_solice"' not in base
    assert 'href="/tower"' in base
    assert "Private Entry" in base

    result = {
        "pack": "029",
        "status": "passed",
        "human_reason": "Owner access launcher creates temporary door-specific Tower URLs and the base entry link no longer hardcodes an unkeyed command dashboard route.",
    }
    _print("PACK 029 RESULT", result)
    return result


if __name__ == "__main__":
    run_tests()
