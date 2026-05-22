
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

from tower.ob_object_guard import evaluate_ob_object_guard
from web.app import app


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _preview(resp):
    body = resp.get_data(as_text=True)[:280]
    return {"status": resp.status_code, "preview": body}


def run_tests():
    registered = getattr(app, "_pack050_symbol_object_guard_registered", False)
    _print("SYMBOL OBJECT GUARD REGISTERED", {"registered": registered})
    assert registered is True

    # Direct object guard still works.
    direct_owner = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="symbol",
        object_id="AAPL",
        action="view",
        route_key="symbol_detail",
    )
    _print("DIRECT OWNER SYMBOL", direct_owner)
    assert direct_owner.get("allowed") is True

    direct_beta = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="symbol",
        object_id="AAPL",
        action="view",
        route_key="symbol_detail",
    )
    _print("DIRECT BETA SYMBOL", direct_beta)
    assert direct_beta.get("allowed") is False

    client = app.test_client()

    # Beta user should get object-locked page on symbol detail.
    beta_resp = client.get("/signals/AAPL?ob_user_id=beta_001&ob_role=user")
    beta_body = beta_resp.get_data(as_text=True)
    _print("BETA SYMBOL ROUTE", _preview(beta_resp))
    assert beta_resp.status_code == 403
    assert "Private drawer locked" in beta_body or "Private corridor locked" in beta_body
    assert "AAPL" in beta_body

    # Owner should not be blocked by Pack 050 object guard.
    # Underlying app route may be 200/302/404 depending on current app internals,
    # but it should not be the object guard locked page.
    owner_resp = client.get("/signals/AAPL?ob_user_id=owner_solice&ob_role=owner")
    owner_body = owner_resp.get_data(as_text=True)
    _print("OWNER SYMBOL ROUTE", _preview(owner_resp))
    assert not (
        owner_resp.status_code == 403
        and "Private drawer locked" in owner_body
    )

    # Non-symbol route should not be handled by symbol object guard.
    login_resp = client.get("/login")
    _print("LOGIN ROUTE", _preview(login_resp))
    assert "Private drawer locked" not in login_resp.get_data(as_text=True)

    # Symbol extraction should also catch /symbol/AAPL if the route exists later.
    symbol_resp = client.get("/symbol/AAPL?ob_user_id=beta_001&ob_role=user")
    symbol_body = symbol_resp.get_data(as_text=True)
    _print("GENERIC SYMBOL ROUTE", _preview(symbol_resp))
    assert symbol_resp.status_code == 403
    assert "AAPL" in symbol_body

    serialized = json.dumps(
        [direct_owner, direct_beta],
        sort_keys=True,
        default=str,
    )
    assert "tower_keycard=" not in serialized
    assert "raw_token" not in serialized
    assert "Soulaana:" in serialized

    final = {
        "pack": "050",
        "status": "passed",
        "human_reason": "Symbol detail-style routes now pass through the OB object guard so exact symbol drawers require object clearance.",
    }
    _print("PACK 050 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
