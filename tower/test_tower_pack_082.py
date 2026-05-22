
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
    if name == "web.app" or name == "web" or name == "tower" or name.startswith("tower."):
        sys.modules.pop(name, None)

from web.app import app
from tower.deny_path_replacement_audit import (
    record_deny_path_replacement_receipt,
    summarize_deny_path_replacement_receipts,
)


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _assert_polished_no_access(html):
    assert "<!doctype html>" in html
    assert "The Tower" in html
    assert "Clearance Gate" in html
    assert "Restricted Zone" in html
    assert "Observatory Corridor Locked" in html
    assert "legacy no-access shell has been replaced" in html or "old no-access shell is retired" in html
    assert "Soulaana:" in html
    assert "request_observatory_clearance" in html
    assert "<title>Observatory Locked</title>" not in html
    assert "tower_keycard=" not in html
    assert "SHOULD_NOT_SURVIVE" not in html
    assert "raw_token=" not in html
    assert '"raw_token":' not in html
    assert "Bearer SHOULD_NOT_SURVIVE" not in html


def run_tests():
    before = summarize_deny_path_replacement_receipts(limit=5)
    _print("BEFORE DENY REPLACEMENT SUMMARY", before)

    client = app.test_client()

    resp = client.get("/no-access?path=/signals?tower_keycard=SHOULD_NOT_SURVIVE")
    html = resp.get_data(as_text=True)

    _print("NO-ACCESS REPLACEMENT RESPONSE", {
        "status": resp.status_code,
        "preview": html[:360],
        "has_tower": "The Tower" in html,
        "has_clearance_gate": "Clearance Gate" in html,
        "has_old_shell_title": "<title>Observatory Locked</title>" in html,
        "has_legacy_replaced_language": "legacy no-access shell has been replaced" in html or "old no-access shell is retired" in html,
    })

    assert resp.status_code == 403
    _assert_polished_no_access(html)

    proof = {
        "ok": True,
        "status_code": resp.status_code,
        "route_path": "/no-access",
        "requested_path": "/signals",
        "has_tower": "The Tower" in html,
        "has_clearance_gate": "Clearance Gate" in html,
        "has_restricted_zone": "Restricted Zone" in html,
        "has_polished_title": "Observatory Corridor Locked" in html,
        "has_replaced_language": "legacy no-access shell has been replaced" in html or "old no-access shell is retired" in html,
        "old_shell_absent": "<title>Observatory Locked</title>" not in html,
        "no_keycard_query": "tower_keycard=" not in html,
        "no_test_secret": "SHOULD_NOT_SURVIVE" not in html,
    }

    receipt = record_deny_path_replacement_receipt(
        route_path="/no-access",
        replacement_type="polished_tower_locked_page",
        old_behavior="legacy_no_access_shell",
        new_behavior="tower_polished_locked_helper",
        actor_user_id="owner_solice",
        reason="Pack 082 replaced the real legacy /no-access shell with the polished Tower locked helper.",
        proof=proof,
        metadata={
            "pack": "082",
            "target": "/no-access",
            "safe_note": "first real legacy no-access path replacement",
            "tower_keycard": "SHOULD_NOT_SURVIVE",
            "raw_token": "SHOULD_NOT_SURVIVE",
        },
    )

    _print("DENY REPLACEMENT RECEIPT", receipt)

    assert receipt.get("ok") is True
    assert receipt.get("status") == "verified"
    assert receipt.get("route_path") == "/no-access"
    assert receipt.get("proof", {}).get("status_code") == 403
    assert receipt.get("proof", {}).get("old_shell_absent") is True

    after = summarize_deny_path_replacement_receipts(limit=12)
    _print("AFTER DENY REPLACEMENT SUMMARY", after)

    assert after.get("ok") is True
    assert after.get("total", 0) >= before.get("total", 0) + 1
    assert after.get("verified", 0) >= 1
    assert after.get("by_route", {}).get("/no-access", 0) >= 1
    assert after.get("by_replacement_type", {}).get("polished_tower_locked_page", 0) >= 1

    serialized = json.dumps([receipt, after], sort_keys=True, default=str) + html
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "082",
        "status": "passed",
        "human_reason": "Legacy /no-access shell now renders the polished Tower locked helper and records a replacement receipt.",
    }
    _print("PACK 082 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
