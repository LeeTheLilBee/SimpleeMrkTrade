
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
    list_deny_path_replacement_receipts,
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


def run_tests():
    before = summarize_deny_path_replacement_receipts(limit=5)
    _print("BEFORE DENY REPLACEMENT RECEIPTS", before)

    client = app.test_client()
    resp = client.get("/observatory-private?tower_keycard=SHOULD_NOT_SURVIVE")
    html = resp.get_data(as_text=True)

    proof = {
        "ok": (
            resp.status_code == 403
            and "The Tower" in html
            and "Clearance Gate" in html
            and "Restricted Zone" in html
            and "Observatory Corridor Locked" in html
            and "<title>Observatory Locked</title>" not in html
            and "tower_keycard=" not in html
            and "SHOULD_NOT_SURVIVE" not in html
        ),
        "status_code": resp.status_code,
        "has_tower": "The Tower" in html,
        "has_clearance_gate": "Clearance Gate" in html,
        "has_restricted_zone": "Restricted Zone" in html,
        "has_polished_title": "Observatory Corridor Locked" in html,
        "old_shell_absent": "<title>Observatory Locked</title>" not in html,
        "no_keycard_query": "tower_keycard=" not in html,
        "no_test_secret": "SHOULD_NOT_SURVIVE" not in html,
    }

    receipt = record_deny_path_replacement_receipt(
        route_path="/observatory-private",
        replacement_type="polished_tower_locked_page",
        old_behavior="legacy_ob_private_shell",
        new_behavior="tower_polished_locked_helper",
        actor_user_id="owner_solice",
        reason="Pack 081 records the first controlled deny-path replacement proof.",
        proof=proof,
        metadata={
            "pack": "081",
            "raw_token": "SHOULD_NOT_SURVIVE",
            "tower_keycard": "SHOULD_NOT_SURVIVE",
            "safe_note": "first controlled deny-path receipt",
        },
    )

    _print("RECORDED RECEIPT", receipt)

    assert receipt.get("ok") is True
    assert receipt.get("status") == "verified"
    assert receipt.get("route_path") == "/observatory-private"
    assert receipt.get("proof", {}).get("ok") is True
    assert receipt.get("proof", {}).get("status_code") == 403

    # Add one intentionally incomplete receipt so summary proves needs_review too.
    review_receipt = record_deny_path_replacement_receipt(
        route_path="/future-deny-path",
        replacement_type="polished_tower_locked_page",
        old_behavior="legacy_unknown_shell",
        new_behavior="tower_polished_locked_helper",
        actor_user_id="owner_solice",
        reason="Pack 081 review-path test.",
        proof={
            "ok": False,
            "status_code": 0,
            "raw_token": "SHOULD_NOT_SURVIVE",
        },
        metadata={
            "pack": "081",
            "authorization": "Bearer SHOULD_NOT_SURVIVE",
        },
    )
    _print("REVIEW RECEIPT", review_receipt)
    assert review_receipt.get("status") == "needs_review"

    after = summarize_deny_path_replacement_receipts(limit=10)
    _print("AFTER DENY REPLACEMENT RECEIPTS", after)

    assert after.get("ok") is True
    assert after.get("total", 0) >= before.get("total", 0) + 2
    assert after.get("verified", 0) >= 1
    assert after.get("needs_review", 0) >= 1
    assert after.get("by_route", {}).get("/observatory-private", 0) >= 1
    assert after.get("by_replacement_type", {}).get("polished_tower_locked_page", 0) >= 1

    listed = list_deny_path_replacement_receipts(limit=10)
    _print("LIST DENY REPLACEMENT RECEIPTS", {
        "ok": listed.get("ok"),
        "total": listed.get("total"),
        "recent_count": len(listed.get("recent", [])),
        "path": listed.get("path"),
    })
    assert listed.get("ok") is True

    serialized = json.dumps([receipt, review_receipt, after, listed], sort_keys=True, default=str)
    assert "tower_keycard=" not in serialized
    assert "SHOULD_NOT_SURVIVE" not in serialized
    assert "raw_token=" not in serialized
    assert '"raw_token":' not in serialized
    assert "Bearer SHOULD_NOT_SURVIVE" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "081",
        "status": "passed",
        "human_reason": "Deny-path replacement audit receipts record verified and review-needed replacement events safely.",
    }
    _print("PACK 081 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
