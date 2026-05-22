
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

from tower.ob_private_shell import build_no_access_payload, build_private_outer_shell
from web.app import app


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    html, status = build_private_outer_shell(
        reason_code="test_private",
        message="Testing shell.",
        path="/signals",
        status_code=403,
        show_waitlist_hint=True,
    )
    _print("SHELL HELPER", {
        "status": status,
        "has_private": "Private sky" in html,
        "has_soulaana": "Soulaana:" in html,
        "has_path": "/signals" in html,
    })
    assert status == 403
    assert "Private sky" in html
    assert "Soulaana:" in html

    payload = build_no_access_payload(path="/signals")
    _print("NO ACCESS PAYLOAD", payload)
    assert payload.get("ok") is True
    assert payload.get("status") == "locked"
    assert "Soulaana:" in payload.get("soulaana_translation", "")

    client = app.test_client()

    no_access = client.get("/no-access?path=/signals")
    body = no_access.get_data(as_text=True)
    _print("NO ACCESS ROUTE", {"status": no_access.status_code, "preview": body[:260]})
    assert no_access.status_code == 403
    assert "Private sky" in body
    assert "real Observatory is private" in body or "real system does not live in public" in body

    no_access_json = client.get("/no-access.json?path=/signals")
    json_payload = no_access_json.get_json(silent=True)
    _print("NO ACCESS JSON", {"status": no_access_json.status_code, "json": json_payload})
    assert no_access_json.status_code == 200
    assert json_payload.get("status") == "locked"

    # The main guard still blocks private unmapped routes.
    unmapped = client.get("/some-random-private-route")
    _print("UNMAPPED STILL LOCKED", {"status": unmapped.status_code, "preview": unmapped.get_data(as_text=True)[:220]})
    assert unmapped.status_code == 403

    serialized = json.dumps([payload, json_payload], sort_keys=True, default=str)
    assert "tower_keycard=" not in serialized
    assert "raw_token" not in serialized

    final = {
        "pack": "048",
        "status": "passed",
        "human_reason": "Private outer shell and no-access route provide harmless locked public behavior while the real Observatory remains private.",
    }
    _print("PACK 048 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
