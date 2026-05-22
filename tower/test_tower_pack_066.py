
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
    build_locked_state_payload,
    render_locked_state_html,
    render_locked_state_response,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    payload = build_locked_state_payload(
        lock_type="object",
        title="Symbol Intelligence Locked",
        reason_code="ob_clearance_level_too_low",
        human_reason="User clearance is not high enough for this object.",
        path="/signals/AAPL?tower_keycard=SHOULD_NOT_SURVIVE",
        object_type="symbol",
        object_id="AAPL",
        user_id="beta_001",
        risk_state="restricted",
        risk_score=70,
        required_actions=["upgrade_clearance", "owner_review"],
        soulaana_translation="Soulaana: This drawer stays closed until clearance improves.",
    )

    _print("LOCKED PAYLOAD", payload)

    assert payload.get("ok") is False
    assert payload.get("status") == "locked"
    assert payload.get("status_code") == 403
    assert payload.get("lock_type") == "object"
    assert payload.get("object_id") == "AAPL"
    assert "SHOULD_NOT_SURVIVE" not in json.dumps(payload, sort_keys=True, default=str)
    assert "tower_keycard=" not in json.dumps(payload, sort_keys=True, default=str)

    html = render_locked_state_html(payload)

    assert "<!doctype html>" in html
    assert "The Tower" in html
    assert "Clearance Gate" in html
    assert "CLEARANCE REQUIRED" in html
    assert "Restricted Zone" in html
    assert "Symbol Intelligence Locked" in html
    assert "Soulaana:" in html
    assert "upgrade_clearance" in html
    assert "owner_review" in html
    assert "AAPL" in html
    assert "SHOULD_NOT_SURVIVE" not in html
    assert "tower_keycard=" not in html
    assert "raw_token" not in html

    response_html, status_code, response_payload = render_locked_state_response(
        lock_type="mode",
        title="Live Automated Mode Locked",
        reason_code="ob_mode_automation_authorization_missing",
        human_reason="Automated live mode needs explicit automation authorization.",
        mode_name="live_automated",
        user_id="owner_solice",
        risk_state="restricted",
        risk_score=90,
        required_actions=["owner_automation_authorization", "kill_switch_check", "broker_plugin_check"],
        soulaana_translation="Soulaana: Automated live trading is the locked vault, not the lobby.",
    )

    assert status_code == 403
    assert response_payload.get("mode_name") == "live_automated"
    assert "Live Automated Mode Locked" in response_html
    assert "owner_automation_authorization" in response_html
    assert "kill_switch_check" in response_html
    assert "broker_plugin_check" in response_html

    final = {
        "pack": "066",
        "status": "passed",
        "human_reason": "Polished Tower locked-state template system renders safe premium locked pages with route/object/mode context and no secret leakage.",
    }
    _print("PACK 066 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
