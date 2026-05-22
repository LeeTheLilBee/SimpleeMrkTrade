
from __future__ import annotations
import json, os, sys
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

for name in list(sys.modules.keys()):
    if name == "tower" or name.startswith("tower.") or name == "web.app":
        sys.modules.pop(name, None)

from web.app import app
from tower.ob_object_guard import evaluate_ob_object_guard
from tower.ob_route_guard import match_ob_guard_policy

def _print(title, payload=None):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))

def _preview(resp):
    return {"status": resp.status_code, "preview": resp.get_data(as_text=True)[:260]}

def run_tests():
    assert getattr(app, "_pack051_trade_position_object_guard_registered", False) is True

    match = match_ob_guard_policy("/my-positions/pos_051")
    _print("DYNAMIC POSITION ROUTE MATCH", match)
    assert match.get("match_type") == "dynamic_position_or_trade"

    owner = evaluate_ob_object_guard(user_id="owner_solice", role="owner", object_kind="position", object_id="pos_051", owner_user_id="owner_solice", route_key="positions")
    _print("DIRECT OWNER POSITION", owner)
    assert owner.get("allowed") is True

    beta = evaluate_ob_object_guard(user_id="beta_001", role="user", object_kind="position", object_id="pos_051", owner_user_id="owner_solice", route_key="positions")
    _print("DIRECT BETA POSITION", beta)
    assert beta.get("allowed") is False

    client = app.test_client()

    beta_resp = client.get("/my-positions/pos_051?ob_user_id=beta_001&ob_role=user&owner_user_id=owner_solice")
    _print("BETA POSITION ROUTE", _preview(beta_resp))
    assert beta_resp.status_code == 403
    assert "pos_051" in beta_resp.get_data(as_text=True)

    owner_resp = client.get("/my-positions/pos_051?ob_user_id=owner_solice&ob_role=owner&owner_user_id=owner_solice")
    _print("OWNER POSITION ROUTE", _preview(owner_resp))
    assert not (owner_resp.status_code == 403 and "Private drawer locked" in owner_resp.get_data(as_text=True))

    final = {"pack": "051", "status": "passed", "human_reason": "Trade and position detail-style routes now pass through the OB object guard."}
    _print("PACK 051 RESULT", final)
    return final

if __name__ == "__main__":
    run_tests()
