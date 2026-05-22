
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

from tower.ob_object_guard import evaluate_ob_object_guard
from tower.security_command_page import generate_security_command_dashboard


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    decision = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="export",
        object_id="export_063",
        action="download",
        route_key="export",
        current_risk_score=5,
    )
    _print("FRESH OBJECT DECISION", decision)
    assert decision.get("allowed") is False

    dashboard = generate_security_command_dashboard()
    _print("DASHBOARD RESULT", {
        "ok": dashboard.get("ok"),
        "path": dashboard.get("path"),
        "bytes": dashboard.get("bytes"),
        "object_inbox_ok": dashboard.get("ob_object_security_inbox_ok"),
        "object_inbox_total": dashboard.get("ob_object_security_inbox_total"),
    })

    assert dashboard.get("ok") is True
    html_path = Path(dashboard.get("path", ""))
    assert html_path.exists()

    html = html_path.read_text(encoding="utf-8", errors="replace")

    assert "OB OBJECT SECURITY INBOX" in html
    assert "Drawer Review Queue" in html
    assert 'data-pack="063"' in html
    assert "/tower/security-command/object-inbox/action" in html
    assert 'name="inbox_item_id"' in html
    assert 'name="action_type"' in html
    assert 'value="reviewing"' in html
    assert 'value="resolve"' in html
    assert 'value="ignore"' in html
    assert "Add Note" in html
    assert "Mark Reviewing" in html
    assert "Resolve" in html
    assert "Ignore" in html
    assert "export_063" in html or "export_" in html

    serialized = json.dumps(dashboard, sort_keys=True, default=str) + html
    assert "raw_token" not in serialized
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized

    final = {
        "pack": "063",
        "status": "passed",
        "human_reason": "Tower Security Command UI now renders object inbox action forms for note, reviewing, resolve, and ignore.",
    }
    _print("PACK 063 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
