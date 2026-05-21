
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

from tower.keycard_issuer import (
    build_tower_open_urls,
    get_tower_door_catalog,
    issue_owner_tower_access_urls,
    issue_owner_tower_keycard_bundle,
    issue_tower_route_keycard,
)
from web.app import app


def _print(title, payload=None):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def run_tests():
    client = app.test_client()

    _print("DOOR CATALOG")
    catalog = get_tower_door_catalog()
    _print("catalog", catalog)
    assert catalog["ok"] is True
    assert "command" in catalog["doors"]
    assert catalog["doors"]["regenerate"]["clearance_level"] == "critical"

    _print("NON-OWNER CANNOT ISSUE")
    denied = issue_tower_route_keycard(
        actor_user_id="beta_001",
        target_user_id="beta_001",
        door_key="command",
        reason="Beta should not issue.",
    )
    _print("denied", denied)
    assert denied["ok"] is False
    assert denied["reason_code"] == "owner_keycard_issuer_required"

    _print("UNKNOWN DOOR DENIED")
    bad_door = issue_tower_route_keycard(
        actor_user_id="owner_solice",
        target_user_id="owner_solice",
        door_key="not_a_real_door",
        reason="Bad door test.",
    )
    _print("bad door", bad_door)
    assert bad_door["ok"] is False
    assert bad_door["reason_code"] == "unknown_tower_door"

    _print("ISSUE COMMAND PASS")
    command = issue_tower_route_keycard(
        actor_user_id="owner_solice",
        target_user_id="owner_solice",
        door_key="command",
        reason="Pack 027 command pass test.",
        session_id="session_pack027",
        device_id="device_pack027",
    )
    _print("command", {k: command.get(k) for k in ["ok", "pass_id", "token_preview", "expires_at"]})
    assert command["ok"] is True
    assert command["door"]["door_id"] == "/tower/security-command"

    query = (
        f"tower_user_id=owner_solice"
        f"&tower_keycard={command['token']}"
        f"&tower_session_id=session_pack027"
        f"&tower_device_id=device_pack027"
    )

    response = client.get("/tower/security-command?" + query)
    _print("command route response", {"status": response.status_code, "preview": response.get_data(as_text=True)[:260]})
    assert response.status_code == 200

    wrong_response = client.get("/tower/status.json?" + query)
    _print("wrong route with command token", {"status": wrong_response.status_code, "json": wrong_response.get_json(silent=True)})
    assert wrong_response.status_code == 403
    assert wrong_response.get_json(silent=True)["ok"] is False

    _print("ISSUE OWNER BUNDLE")
    bundle = issue_owner_tower_keycard_bundle(
        actor_user_id="owner_solice",
        target_user_id="owner_solice",
        reason="Pack 027 owner bundle test.",
        session_id="session_pack027_bundle",
        device_id="device_pack027_bundle",
        include_regenerate=True,
    )
    _print("bundle", {
        "ok": bundle.get("ok"),
        "issued_keys": sorted(bundle.get("issued", {}).keys()),
        "failures": bundle.get("failures"),
    })
    assert bundle["ok"] is True
    assert sorted(bundle["issued"].keys()) == ["command", "entry", "regenerate", "status"]

    urls = build_tower_open_urls(bundle=bundle)
    _print("urls", {"ok": urls["ok"], "url_keys": sorted(urls["urls"].keys())})
    assert urls["ok"] is True
    assert "command" in urls["urls"]
    assert "tower_keycard=" in urls["urls"]["command"]

    status_url = urls["urls"]["status"]
    response = client.get(status_url)
    payload = response.get_json(silent=True)
    _print("status url response", {"status": response.status_code, "json_ok": bool(payload and payload.get("ok"))})
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert payload.get("ok") is True
    assert "security_inbox_total" in payload

    regen_url = urls["urls"]["regenerate"]
    response = client.post(regen_url)
    payload = response.get_json(silent=True)
    _print("regenerate url response", {"status": response.status_code, "json": payload})
    assert response.status_code in (200, 500)
    assert isinstance(payload, dict)
    assert payload.get("reason_code") != "tower_keycard_required"

    _print("ISSUE OWNER ACCESS URLS CONVENIENCE")
    access = issue_owner_tower_access_urls(
        actor_user_id="owner_solice",
        target_user_id="owner_solice",
        reason="Pack 027 convenience URL test.",
        session_id="session_pack027_urls",
        device_id="device_pack027_urls",
        include_regenerate=False,
    )
    _print("access", {"ok": access.get("ok"), "url_keys": sorted(access.get("urls", {}).keys())})
    assert access["ok"] is True
    assert sorted(access["urls"].keys()) == ["command", "entry", "status"]

    result = {
        "pack": "027",
        "status": "passed",
        "human_reason": "Owner keycard issuer works. It creates separate scoped passes and convenience URLs for protected Tower doors.",
    }
    _print("PACK 027 RESULT", result)
    return result


if __name__ == "__main__":
    run_tests()
