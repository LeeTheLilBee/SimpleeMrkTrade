
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
    if name == "web.app" or name == "web" or name.startswith("tower."):
        sys.modules.pop(name, None)

from web.app import app, _pack068_tower_locked_response
from tower.locked_state_templates import render_route_locked_response


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _assert_polished_locked_html(html):
    assert "<!doctype html>" in html
    assert "The Tower" in html
    assert "Clearance Gate" in html
    assert "Restricted Zone" in html
    assert "Observatory Corridor Locked" in html
    assert "Soulaana:" in html
    assert "tower_keycard=" not in html
    assert "SHOULD_NOT_SURVIVE" not in html
    assert "raw_token=" not in html
    assert '"raw_token":' not in html
    assert "Bearer SHOULD_NOT_SURVIVE" not in html


def run_tests():
    # Direct template remains healthy.
    direct_html, direct_status, direct_payload = render_route_locked_response(
        path="/observatory-private?tower_keycard=SHOULD_NOT_SURVIVE",
        reason_code="observatory_private_outer_shell",
        human_reason="The Observatory is private.",
        user_id="anonymous",
    )
    _print("DIRECT ROUTE TEMPLATE", {
        "status": direct_status,
        "payload": direct_payload,
        "preview": direct_html[:240],
    })
    assert direct_status == 403
    _assert_polished_locked_html(direct_html)

    # Flask helper remains healthy.
    helper_html, helper_status = _pack068_tower_locked_response(
        lock_type="route",
        path="/observatory-private?tower_keycard=SHOULD_NOT_SURVIVE",
        user_id="anonymous",
        reason_code="observatory_private_outer_shell",
        human_reason="The Observatory is private.",
        required_actions=["return_to_tower_entry", "request_observatory_clearance"],
        soulaana_translation="Soulaana: No clearance, no corridor.",
    )
    _print("HELPER ROUTE LOCK", {
        "status": helper_status,
        "preview": helper_html[:240],
    })
    assert helper_status == 403
    _assert_polished_locked_html(helper_html)

    # First controlled replacement route.
    client = app.test_client()
    resp = client.get("/observatory-private?tower_keycard=SHOULD_NOT_SURVIVE")
    html = resp.get_data(as_text=True)

    _print("CONTROLLED DENY-PATH ROUTE RESPONSE", {
        "status": resp.status_code,
        "preview": html[:300],
        "has_tower": "The Tower" in html,
        "has_clearance_gate": "Clearance Gate" in html,
        "has_private_language": "private Observatory wall" in html or "The Observatory is private" in html,
        "has_old_plain_shell": "<title>Observatory Locked</title>" in html,
    })

    assert resp.status_code == 403
    _assert_polished_locked_html(html)
    assert "The Observatory is private" in html
    assert "request_observatory_clearance" in html
    assert "keep_private_surface_closed" in html
    assert "<title>Observatory Locked</title>" not in html

    final = {
        "pack": "079",
        "status": "passed",
        "human_reason": "First controlled deny-path replacement route renders the polished Tower locked page safely.",
    }
    _print("PACK 079 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
