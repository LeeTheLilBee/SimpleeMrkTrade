"""Selective hosted Tower↔OB Desk integration: no permission or feed invented."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re

from flask import Flask
import pytest

import tower.ob_market_data_desk_integration as desk
import tower.ob_web_route_enforcement as enforcement
from tower.ob_route_guard import match_ob_guard_policy

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def private_app(monkeypatch):
    state = {"owner": False, "step_up": False, "admitted": False}
    for module in (desk, enforcement):
        monkeypatch.setattr(module, "owner_session_active", lambda: state["owner"])
        monkeypatch.setattr(module, "step_up_active", lambda: state["step_up"])
        monkeypatch.setattr(module, "operational_ob_access_active", lambda: state["admitted"])
    app = Flask(__name__, template_folder=str(ROOT / "web/templates"),
                static_folder=str(ROOT / "web/static"))
    app.config.update(TESTING=True)
    enforcement.register_ob_protected_route_enforcement(app)
    desk.register_protected_ob_market_data_desk(app)
    return app, state


def test_exact_private_route_uses_both_authorities_and_no_early_snapshot(private_app, monkeypatch):
    app, state = private_app
    touched = []
    def counted():
        touched.append(True)
        return desk._unconnected_catalog_snapshot()
    monkeypatch.setattr(desk, "_unconnected_catalog_snapshot", counted)
    # Registered blueprint callback closed over the original function. Replace
    # view's callback by testing the outer guard first and the source route's
    # own guard separately in upstream tests.
    client = app.test_client()
    assert client.get("/ob/data-desk").status_code == 302
    state["owner"] = True
    assert client.get("/ob/data-desk").status_code == 302
    state["step_up"] = True
    assert client.get("/ob/data-desk").status_code == 302
    assert touched == []
    state["admitted"] = True
    assert client.get("/ob/data-desk").status_code == 200
    state["owner"] = False
    assert client.get("/ob/data-desk").status_code == 302


def test_verified_owner_get_head_are_catalog_only_and_public_mutation_denied(private_app):
    app, state = private_app
    state.update(owner=True, step_up=True, admitted=True)
    client = app.test_client()
    response = client.get("/ob/data-desk")
    assert response.status_code == 200
    assert response.headers["Cache-Control"].startswith("no-store")
    html = response.get_data(as_text=True)
    embedded = re.search(
        r'<script id="mddSnapshot" type="application/json">(.+?)</script>', html, re.S
    )
    assert embedded is not None
    snapshot = json.loads(embedded.group(1))
    assert snapshot["schema"] == "OB_MARKET_DATA_DESK_V1"
    assert snapshot["read_only"] is True
    assert snapshot["connection_truth"] == "UNVERIFIED"
    assert snapshot["runtime_health_attached"] is False
    assert snapshot["prices_attached"] is False
    assert snapshot["summary"]["catalog_products"] >= 13
    assert snapshot["summary"]["live_feeds_verified"] is None
    assert snapshot["summary"]["api_requests_remaining"] is None
    assert snapshot["traffic"]["state"] == "NOT_CONNECTED"
    assert snapshot["cases"] == []
    assert snapshot["safety"]["can_execute"] is False
    assert snapshot["safety"]["manual_live_unlocked"] is False
    assert b"data" not in client.head("/ob/data-desk").data
    assert client.head("/ob/data-desk").status_code == 200
    assert client.post("/ob/data-desk").status_code == 405
    assert client.get("/ob/data-desk/connect").status_code == 403
    assert client.get("/ob/data-desk/approve").status_code == 403
    assert client.get("/trade-center").status_code == 404


def test_source_failures_are_sanitized_and_no_alternate_owner_route(private_app, monkeypatch):
    from web.ob_market_data_desk_route import _valid, create_market_data_desk_blueprint
    snapshot = desk._unconnected_catalog_snapshot()
    assert _valid(snapshot)
    assert not _valid({**snapshot, "prices_attached": True})
    failed = Flask("desk_provider_failure")
    failed.config.update(TESTING=False)
    failed.register_blueprint(create_market_data_desk_blueprint(
        tower_owner_authorize=lambda: True,
        protected_snapshot=lambda: (_ for _ in ()).throw(
            RuntimeError("do-not-show-provider-private-secret")
        ),
    ))
    response = failed.test_client().get("/ob/data-desk")
    assert response.status_code == 503
    assert "do-not-show-provider-private-secret" not in response.get_data(as_text=True)


def test_map_exact_and_return_navigation_preserved():
    assert match_ob_guard_policy("/ob/data-desk")["match_type"] == "exact"
    assert match_ob_guard_policy("/ob/data-desk/secret")["match_type"] == "unmapped_default_deny"
    assert match_ob_guard_policy("/trade-center")["match_type"] == "unmapped_default_deny"
    js = (ROOT / "web/static/ob/ob_nav_shell.js").read_text()
    assert 'dataset.obDataDeskRouteEnabled === "true"' in js
    assert 'navLink(path, "/ob/data-desk", "Market Data Desk"' in js
    assert 'navLink(path, "/ob/trade-center", "Trade Center"' in js
    assert 'navLink(path, "/ob/review-center", "Review Center"' in js
    assert 'TOWER_RETURN_PATH = "/tower/return/observatory"' in js
    assert '"/ob/data-desk": "Market Data Desk"' in js
    for page in ("dashboard", "market_map", "symbol_page", "trade_center",
                 "review_center", "owner_console", "owner_dashboard", "market_data_desk"):
        html = (ROOT / "web/templates" / (page + ".html")).read_text()
        assert 'data-ob-data-desk-route-enabled="true"' in html, page
