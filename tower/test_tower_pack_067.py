
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
    if name == "tower" or name.startswith("tower."):
        sys.modules.pop(name, None)

from tower.locked_state_templates import (
    render_decision_locked_response,
    render_export_locked_response,
    render_mode_locked_response,
    render_object_locked_response,
    render_route_locked_response,
    render_unmapped_locked_response,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _assert_safe(html, payload):
    serialized = html + json.dumps(payload, sort_keys=True, default=str)
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "tower_keycard=" not in serialized
    assert "raw_token" not in serialized
    assert "Bearer " not in serialized


def run_tests():
    route_html, route_status, route_payload = render_route_locked_response(
        path="/signals?tower_keycard=SHOULD_NOT_SURVIVE",
        reason_code="ob_clearance_level_too_low",
        human_reason="Signals needs confidential clearance.",
        user_id="beta_001",
    )
    _print("ROUTE PAYLOAD", route_payload)
    assert route_status == 403
    assert route_payload.get("lock_type") == "route"
    assert "Observatory Corridor Locked" in route_html
    assert "request_route_clearance" in route_html
    _assert_safe(route_html, route_payload)

    object_html, object_status, object_payload = render_object_locked_response(
        object_type="symbol",
        object_id="AAPL",
        path="/signals/AAPL",
        reason_code="parent_route_clearance_failed",
        human_reason="The parent route was not cleared.",
        user_id="beta_001",
    )
    assert object_status == 403
    assert object_payload.get("lock_type") == "object"
    assert object_payload.get("object_id") == "AAPL"
    assert "Symbol Locked" in object_html
    assert "request_object_clearance" in object_html
    _assert_safe(object_html, object_payload)

    mode_html, mode_status, mode_payload = render_mode_locked_response(
        mode_name="live_automated",
        reason_code="ob_mode_automation_authorization_missing",
        human_reason="Automated live mode needs explicit automation authorization.",
        user_id="owner_solice",
    )
    assert mode_status == 403
    assert mode_payload.get("lock_type") == "mode"
    assert "Live Automated Locked" in mode_html
    assert "complete_required_authorization" in mode_html
    assert "owner_automation_authorization" not in mode_html  # not passed here
    _assert_safe(mode_html, mode_payload)

    export_html, export_status, export_payload = render_export_locked_response(
        export_id="export_067",
        path="/export",
        user_id="beta_001",
    )
    assert export_status == 403
    assert export_payload.get("lock_type") == "export"
    assert export_payload.get("object_type") == "export"
    assert "Export Locked" in export_html
    assert "request_export_clearance" in export_html
    _assert_safe(export_html, export_payload)

    unmapped_html, unmapped_status, unmapped_payload = render_unmapped_locked_response(
        path="/new-secret-page",
        object_type="mystery",
        object_id="unknown_067",
        user_id="owner_solice",
    )
    assert unmapped_status == 403
    assert unmapped_payload.get("lock_type") == "unmapped"
    assert "Unmapped Corridor Locked" in unmapped_html
    assert "keep_default_deny_until_mapped" in unmapped_html
    _assert_safe(unmapped_html, unmapped_payload)

    decision_html, decision_status, decision_payload = render_decision_locked_response(
        decision={
            "allowed": False,
            "decision": "deny",
            "reason_code": "ob_mode_automation_authorization_missing",
            "human_reason": "Automated live mode needs explicit automation authorization.",
            "risk_state": "restricted",
            "risk_score": 90,
            "required_actions": [
                "owner_automation_authorization",
                "kill_switch_check",
                "broker_plugin_check",
            ],
            "metadata": {
                "user_id": "owner_solice",
                "mode_name": "live_automated",
            },
            "soulaana_translation": "Soulaana: Automated live trading is the locked vault, not the lobby.",
        }
    )
    assert decision_status == 403
    assert decision_payload.get("lock_type") == "mode"
    assert decision_payload.get("mode_name") == "live_automated"
    assert "owner_automation_authorization" in decision_html
    assert "kill_switch_check" in decision_html
    _assert_safe(decision_html, decision_payload)

    final = {
        "pack": "067",
        "status": "passed",
        "human_reason": "Route/object/mode/export/unmapped locked-state variants render safe Tower-branded blocked pages.",
    }
    _print("PACK 067 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
