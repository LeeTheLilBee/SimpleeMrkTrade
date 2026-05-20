
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Clear stale modules so web.app imports the newly written web_bridge.
for name in list(sys.modules.keys()):
    if name == "tower" or name.startswith("tower.") or name == "web.app":
        sys.modules.pop(name, None)

from tower.keycard_passes import issue_keycard_pass
from web.app import app


def _print(title, payload=None):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))


def _body(response):
    return response.get_data(as_text=True)


def _assert_locked_html(response):
    assert response.status_code == 403, response.status_code
    text = _body(response)
    assert "Clearance required" in text
    assert "Security Command Dashboard" not in text
    assert "security_inbox_total" not in text
    assert "owner_solice" not in text


def _assert_locked_json(response):
    assert response.status_code == 403, response.status_code
    payload = response.get_json(silent=True)
    assert isinstance(payload, dict), payload
    assert payload.get("ok") is False
    assert payload.get("reason_code")
    assert "security_inbox_total" not in payload
    assert "total_users" not in payload
    assert "owner_solice" not in json.dumps(payload)


def _issue(
    *,
    door_id,
    actions=("view",),
    clearance_level="restricted",
    ttl_seconds=900,
    session_id="session_owner_026",
    device_id="device_owner_026",
):
    return issue_keycard_pass(
        user_id="owner_solice",
        app_name="tower",
        door_type="route",
        door_id=door_id,
        actions=list(actions),
        issuer_user_id="owner_solice",
        reason=f"Pack 026 test pass for {door_id}.",
        ttl_seconds=ttl_seconds,
        session_id=session_id,
        device_id=device_id,
        role="owner",
        clearance_level=clearance_level,
        risk_score_at_issue=5,
    )


def _query(token):
    return (
        "tower_user_id=owner_solice"
        f"&tower_keycard={token}"
        "&tower_session_id=session_owner_026"
        "&tower_device_id=device_owner_026"
    )


def run_tests():
    client = app.test_client()

    routes = sorted(str(rule.rule) for rule in app.url_map.iter_rules() if str(rule.rule).startswith("/tower"))
    _print("TOWER ROUTES", routes)

    required = [
        "/tower",
        "/tower/",
        "/tower/security-command",
        "/tower/security-command/regenerate",
        "/tower/status.json",
    ]
    missing = [route for route in required if route not in routes]
    assert not missing, missing

    _print("UNAUTHORIZED HTML ROUTES SHOULD LOCK")
    for path in ["/tower", "/tower/", "/tower/security-command"]:
        response = client.get(path)
        _print(path, {"status": response.status_code, "preview": _body(response)[:220]})
        _assert_locked_html(response)

    _print("UNAUTHORIZED STATUS JSON SHOULD LOCK WITHOUT METRICS")
    response = client.get("/tower/status.json")
    _print("/tower/status.json", {"status": response.status_code, "json": response.get_json(silent=True)})
    _assert_locked_json(response)

    _print("ISSUE COMMAND KEYCARD")
    command_pass = _issue(door_id="/tower/security-command")
    command_token = command_pass["token"]
    _print("command pass", {"pass_id": command_pass["pass_id"], "preview": command_pass["token_preview"]})

    response = client.get("/tower/security-command?" + _query(command_token))
    _print("AUTHORIZED COMMAND", {"status": response.status_code, "preview": _body(response)[:320]})
    assert response.status_code == 200
    assert "Security Command Dashboard" in _body(response) or "The Tower" in _body(response)

    _print("COMMAND KEYCARD MUST NOT OPEN STATUS JSON")
    response = client.get("/tower/status.json?" + _query(command_token))
    _print("wrong door status response", {"status": response.status_code, "json": response.get_json(silent=True)})
    _assert_locked_json(response)

    _print("ISSUE STATUS KEYCARD")
    status_pass = _issue(door_id="/tower/status.json")
    status_token = status_pass["token"]
    response = client.get("/tower/status.json?" + _query(status_token))
    payload = response.get_json(silent=True)
    _print(
        "AUTHORIZED STATUS JSON",
        {
            "status": response.status_code,
            "json_ok": bool(payload and payload.get("ok")),
            "has_metrics": isinstance(payload, dict) and "security_inbox_total" in payload,
        },
    )
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert payload.get("ok") is True
    assert "security_inbox_total" in payload

    _print("ISSUE ENTRY KEYCARD")
    entry_pass = _issue(door_id="/tower")
    entry_token = entry_pass["token"]
    response = client.get("/tower?" + _query(entry_token))
    _print("AUTHORIZED ENTRY", {"status": response.status_code, "preview": _body(response)[:320]})
    assert response.status_code == 200
    assert "The Tower" in _body(response)
    assert "Open Security Command" in _body(response)

    _print("ISSUE REGENERATE KEYCARD")
    regen_pass = _issue(
        door_id="/tower/security-command/regenerate",
        actions=("regenerate",),
        clearance_level="critical",
    )
    regen_token = regen_pass["token"]
    response = client.post("/tower/security-command/regenerate?" + _query(regen_token))
    payload = response.get_json(silent=True)
    _print("AUTHORIZED REGENERATE", {"status": response.status_code, "json": payload})
    assert response.status_code in (200, 500)
    assert isinstance(payload, dict)
    assert payload.get("reason_code") != "tower_keycard_required"

    result = {
        "pack": "026",
        "status": "passed",
        "human_reason": "Tower private front door gate is active. Routes require exact scoped keycard passes and locked responses do not leak metrics.",
        "protected_routes": required,
    }
    _print("PACK 026 RESULT", result)
    return result


if __name__ == "__main__":
    run_tests()
