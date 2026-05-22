
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
    assert getattr(app, "_pack052_export_object_guard_registered", False) is True

    match = match_ob_guard_policy("/export")
    _print("EXPORT ROUTE MATCH", match)
    assert match.get("policy", {}).get("route_key") == "export"

    owner = evaluate_ob_object_guard(user_id="owner_solice", role="owner", object_kind="export", object_id="export_052", action="download", route_key="export")
    _print("DIRECT OWNER EXPORT", owner)
    assert owner.get("allowed") is True

    beta = evaluate_ob_object_guard(user_id="beta_001", role="user", object_kind="export", object_id="export_052", action="download", route_key="export")
    _print("DIRECT BETA EXPORT", beta)
    assert beta.get("allowed") is False

    client = app.test_client()

    beta_resp = client.get("/export?export_id=export_052&ob_user_id=beta_001&ob_role=user")
    beta_body = beta_resp.get_data(as_text=True)
    _print("BETA EXPORT ROUTE", _preview(beta_resp))
    assert beta_resp.status_code == 403
    assert (
        "Private corridor locked" in beta_body
        or "Private drawer locked" in beta_body
        or "Observatory Locked" in beta_body
    )

    owner_resp = client.get("/export?export_id=export_052&ob_user_id=owner_solice&ob_role=owner")
    owner_body = owner_resp.get_data(as_text=True)
    _print("OWNER EXPORT ROUTE", _preview(owner_resp))
    assert not (
        owner_resp.status_code == 403
        and (
            "Private corridor locked" in owner_body
            or "Private drawer locked" in owner_body
        )
    )

    final = {"pack": "052", "status": "passed", "human_reason": "Export and download-style routes now pass through the OB object guard."}
    _print("PACK 052 RESULT", final)
    return final

if __name__ == "__main__":
    run_tests()
