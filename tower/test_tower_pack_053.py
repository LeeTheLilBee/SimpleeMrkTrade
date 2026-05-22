
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
from tower.ob_mode_clearance import evaluate_ob_mode_clearance

def _print(title, payload=None):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))

def _preview(resp):
    return {"status": resp.status_code, "preview": resp.get_data(as_text=True)[:260]}

def run_tests():
    assert getattr(app, "_pack053_mode_guard_registered", False) is True

    survey = evaluate_ob_mode_clearance(user_id="beta_001", role="user", mode_name="survey", action="enter")
    _print("DIRECT SURVEY", survey)
    assert survey.get("allowed") is True

    live_auto_no_auth = evaluate_ob_mode_clearance(
        user_id="owner_solice",
        role="owner",
        mode_name="live_automated",
        action="enter",
        broker_connected=True,
        broker_healthy=True,
        live_authorized=True,
        automation_authorized=False,
    )
    _print("DIRECT LIVE AUTO NO AUTH", live_auto_no_auth)
    assert live_auto_no_auth.get("allowed") is False

    client = app.test_client()

    survey_resp = client.get("/mode/survey?ob_user_id=beta_001&ob_role=user")
    _print("SURVEY ROUTE", _preview(survey_resp))
    assert not (survey_resp.status_code == 403 and "Private sky" in survey_resp.get_data(as_text=True))

    auto_resp = client.get("/mode/live_automated?ob_user_id=owner_solice&ob_role=owner&broker_connected=true&broker_healthy=true&live_authorized=true&automation_authorized=false")
    auto_body = auto_resp.get_data(as_text=True)
    _print("LIVE AUTO NO AUTH ROUTE", _preview(auto_resp))
    assert auto_resp.status_code == 403
    assert (
        "Private sky" in auto_body
        or "Private corridor locked" in auto_body
        or "Observatory Locked" in auto_body
    )

    lockdown_resp = client.get("/mode/survey?ob_user_id=owner_solice&ob_role=owner&emergency_lockdown=true")
    lockdown_body = lockdown_resp.get_data(as_text=True)
    _print("LOCKDOWN MODE ROUTE", _preview(lockdown_resp))
    assert lockdown_resp.status_code == 403
    assert (
        "Private sky" in lockdown_body
        or "Private corridor locked" in lockdown_body
        or "Observatory Locked" in lockdown_body
    )

    final = {"pack": "053", "status": "passed", "human_reason": "Mode-switch style requests now pass through Tower mode clearance."}
    _print("PACK 053 RESULT", final)
    return final

if __name__ == "__main__":
    run_tests()
