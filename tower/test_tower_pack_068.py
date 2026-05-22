
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


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _assert_locked_html(html):
    assert "The Tower" in html
    assert "Clearance Gate" in html or "Clearance Required" in html
    assert "Restricted Zone" in html or "restricted" in html.lower()
    assert "Soulaana:" in html
    assert "tower_keycard=" not in html
    assert "raw_token" not in html
    assert "SHOULD_NOT_SURVIVE" not in html


def run_tests():
    route_html, route_status = _pack068_tower_locked_response(
        lock_type="route",
        path="/signals?tower_keycard=SHOULD_NOT_SURVIVE",
        user_id="beta_001",
        reason_code="ob_clearance_level_too_low",
        human_reason="Signals needs confidential clearance.",
        required_actions=["upgrade_clearance", "owner_review"],
        soulaana_translation="Soulaana: This corridor is not public. The Tower held the line.",
    )
    _print("ROUTE RESPONSE", {"status": route_status, "preview": route_html[:220]})
    assert route_status == 403
    assert "Observatory Corridor Locked" in route_html
    _assert_locked_html(route_html)

    object_html, object_status = _pack068_tower_locked_response(
        lock_type="object",
        path="/signals/AAPL",
        object_type="symbol",
        object_id="AAPL",
        user_id="beta_001",
        reason_code="parent_route_clearance_failed",
        human_reason="The parent route was not cleared.",
    )
    assert object_status == 403
    assert "Symbol Locked" in object_html
    assert "AAPL" in object_html
    _assert_locked_html(object_html)

    mode_html, mode_status = _pack068_tower_locked_response(
        lock_type="mode",
        mode_name="live_automated",
        user_id="owner_solice",
        reason_code="ob_mode_automation_authorization_missing",
        human_reason="Automated live mode needs explicit automation authorization.",
        required_actions=["owner_automation_authorization", "kill_switch_check"],
        soulaana_translation="Soulaana: Automated live trading is the locked vault, not the lobby.",
    )
    assert mode_status == 403
    assert "Live Automated Locked" in mode_html
    assert "owner_automation_authorization" in mode_html
    _assert_locked_html(mode_html)

    export_html, export_status = _pack068_tower_locked_response(
        lock_type="export",
        export_id="export_068",
        path="/export",
        user_id="beta_001",
    )
    assert export_status == 403
    assert "Export Locked" in export_html
    assert "export_068" in export_html
    _assert_locked_html(export_html)

    decision_html, decision_status = _pack068_tower_locked_response(
        decision={
            "allowed": False,
            "decision": "deny",
            "reason_code": "ob_object_unmapped_default_deny",
            "human_reason": "This object kind is not mapped yet.",
            "risk_state": "restricted",
            "risk_score": 75,
            "required_actions": ["map_object_policy", "owner_review"],
            "metadata": {
                "user_id": "owner_solice",
                "object_type": "mystery",
                "object_id": "secret_068",
            },
            "soulaana_translation": "Soulaana: I do not open objects that are not on the Tower map.",
        },
        path="/secret",
    )
    assert decision_status == 403
    assert "Unmapped Corridor Locked" in decision_html
    assert "secret_068" in decision_html
    _assert_locked_html(decision_html)

    client = app.test_client()
    preview = client.get("/tower/polished-locked-preview?path=/signals?tower_keycard=SHOULD_NOT_SURVIVE")
    preview_html = preview.get_data(as_text=True)
    _print("PREVIEW ROUTE", {"status": preview.status_code, "preview": preview_html[:220]})
    assert preview.status_code == 403
    _assert_locked_html(preview_html)

    final = {
        "pack": "068",
        "status": "passed",
        "human_reason": "web/app.py now has a Tower-branded locked response helper that renders route/object/mode/export/unmapped locked pages safely.",
    }
    _print("PACK 068 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
