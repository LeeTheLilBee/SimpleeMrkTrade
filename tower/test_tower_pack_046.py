
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

from tower.ob_route_guard import evaluate_ob_request_guard
from web.app import app


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _preview(resp):
    body = resp.get_data(as_text=True)[:260]
    return {"status": resp.status_code, "preview": body}


def run_tests():
    registered = getattr(app, "_pack046_ob_route_guard_registered", False)
    _print("GUARD REGISTERED", {"registered": registered})
    assert registered is True

    client = app.test_client()

    # Public-safe route should not be blocked by OB guard.
    login_resp = client.get("/login")
    _print("LOGIN ROUTE", _preview(login_resp))
    assert login_resp.status_code != 403

    # Protected route should block anonymous/internal access.
    blocked_signals = client.get("/signals?ob_user_id=beta_001&ob_role=user")
    _print("BLOCKED SIGNALS", _preview(blocked_signals))
    assert blocked_signals.status_code == 403
    assert "Private corridor locked" in blocked_signals.get_data(as_text=True)

    # Owner should pass the guard. The underlying route may return 200/302/404
    # depending on app internals, but it should not be the guard's locked 403.
    owner_signals = client.get("/signals?ob_user_id=owner_solice&ob_role=owner")
    _print("OWNER SIGNALS", _preview(owner_signals))
    assert not (
        owner_signals.status_code == 403
        and "Private corridor locked" in owner_signals.get_data(as_text=True)
    )

    # Unmapped route should default-deny before normal 404 behavior.
    unmapped = client.get("/brand-new-private-page")
    _print("UNMAPPED ROUTE", _preview(unmapped))
    assert unmapped.status_code == 403
    assert "Unmapped corridor" in unmapped.get_data(as_text=True) or "Private corridor locked" in unmapped.get_data(as_text=True)

    # Tower route should be skipped by OB guard and handled by Tower itself.
    tower_resp = client.get("/tower/security-command")
    _print("TOWER ROUTE", _preview(tower_resp))
    assert tower_resp.status_code in {200, 302, 403}
    assert "Private corridor locked" not in tower_resp.get_data(as_text=True)

    direct_decision = evaluate_ob_request_guard(
        path="/signals",
        user_id="beta_001",
        role="user",
    )
    _print("DIRECT GUARD DECISION", direct_decision)
    assert direct_decision.get("allowed") is False

    final = {
        "pack": "046",
        "status": "passed",
        "human_reason": "Flask before_request now calls the OB route guard, blocks protected/unmapped OB routes, and leaves public-safe/Tower/static routes alone.",
    }
    _print("PACK 046 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
