"""Source truth across keyless, Public and temporary research-key lanes."""
from __future__ import annotations

import json
from pathlib import Path

from flask import Flask
from werkzeug.datastructures import MultiDict
import pytest

from tower.ob_route_guard import match_ob_guard_policy
from tower.ob_web_route_enforcement import PROTECTED_EXACT_OB_ROUTES
from web.ob_connection_truth_route import (
    PATH, connection_status_projection, create_connection_truth_blueprint,
)
import tower.ob_provider_key_desk as keys

ROOT = Path(__file__).resolve().parents[1]
SID = "tower_session_fictional_owner_01234567"
SECRET = "PRIVATE_SYNTHETIC_TEST_CREDENTIAL"


def _key_rows(_sid):
    assert _sid == SID
    return (
        {"id": "finnhub", "name": "Finnhub", "present": True,
         "probe": "READ_ONLY_CHECK_PASSED", "secret": SECRET,
         "expires_at": "2030-01-01T00:00:00+00:00"},
        {"id": "alpha_vantage", "name": "Alpha Vantage", "present": False,
         "probe": "NOT_CONFIGURED", "value": SECRET},
        {"id": "finazon", "name": "Finazon", "present": False,
         "probe": "NOT_CONFIGURED", "secret": SECRET},
        {"id": "eia", "name": "U.S. EIA", "present": False,
         "probe": "NOT_CONFIGURED", "secret": SECRET},
        {"id": "bea", "name": "U.S. BEA", "present": False,
         "probe": "NOT_CONFIGURED", "secret": SECRET},
        {"id": "alpaca", "name": "Alpaca", "present": False,
         "probe": "NOT_CONFIGURED", "secret": SECRET},
    )


def _public(_sid):
    assert _sid == SID
    return {"authentication_temporarily_present": True,
            "account_linked": False, "owner_selection_required": False,
            "access_token": SECRET, "account_id": "private-synthetic-account"}


def test_safe_projection_never_conflates_connection_and_data_license(monkeypatch):
    for k in ("OB_KEYLESS_RESEARCH_ENABLED", "OB_SEC_PUBLIC_RESEARCH_ENABLED"):
        monkeypatch.delenv(k, raising=False)
    result = connection_status_projection(
        sid=SID, key_reader=_key_rows, public_reader=_public,
    )
    assert result["schema"] == "OB_TOWER_PROVIDER_CONNECTION_TRUTH_V1"
    assert result["dissemination_contract"] == "OWNER_STATUS_ONLY"
    assert result["live_feed_count_verified"] is None
    assert result["prices_attached"] is False
    assert result["may_authorize_order"] is False
    assert len(result["provider_status"]) == 11
    states = {x["provider"]: x for x in result["provider_status"]}
    assert states["finnhub"]["state"] == "READ_ONLY_CHECK_PASSED"
    assert states["finnhub"]["source_use_rights_verified"] is False
    assert states["finnhub"]["quote_feed_activated"] is False
    assert states["alpha_vantage"]["state"] == "NOT_CONFIGURED"
    assert states["finazon"]["state"] == "NOT_CONFIGURED"
    assert states["eia"]["state"] == "NOT_CONFIGURED"
    assert states["bea"]["state"] == "NOT_CONFIGURED"
    assert states["public"]["state"] == "TEMPORARY_AUTH_ONLY"
    assert states["public"]["account_linked"] is False
    assert states["bls"]["state"] == "RIGHTS_REVIEW_HOLD"
    assert SECRET not in json.dumps(result)
    assert "private-synthetic-account" not in json.dumps(result)
    assert "expires_at" not in json.dumps(result)
    assert "secret" not in json.dumps(result)


def test_reviewed_keyless_configuration_is_not_a_successful_provider_fetch(monkeypatch):
    monkeypatch.setenv("OB_KEYLESS_RESEARCH_ENABLED", "1")
    monkeypatch.setenv("OB_KEYLESS_BLS_USE_REVIEWED", "1")
    monkeypatch.setenv("OB_KEYLESS_BLS_OWNER_DISPLAY_REVIEWED", "1")
    result = connection_status_projection(sid=SID, key_reader=_key_rows, public_reader=_public)
    states = {x["provider"]: x for x in result["provider_status"]}
    assert states["bls"]["state"] == "USE_AND_OWNER_DISPLAY_CONFIGURED"
    assert states["bls"]["provider_request_made"] is False
    assert states["bls"]["current_data_accepted"] is False
    assert states["bls"]["ai_use_authorized"] is False
    assert states["treasury"]["state"] == "RIGHTS_REVIEW_HOLD"


@pytest.mark.parametrize("reader", [
    lambda s: (), lambda s: [{"id": "finnhub", "present": True,
                                "probe": "READ_ONLY_CHECK_PASSED"}],
    lambda s: [{"id": "finnhub", "present": True, "probe": "NOT_TESTED"}] * 2,
    lambda s: [{"id": "finnhub", "present": True, "probe": "ACTUAL_LIVE_FEED"}],
    lambda s: [{"id": "finnhub", "present": False, "probe": "READ_ONLY_CHECK_PASSED"}],
])
def test_missing_duplicate_or_overstated_key_status_fails_closed(reader):
    with pytest.raises(ValueError):
        connection_status_projection(sid=SID, key_reader=reader, public_reader=_public)


def test_public_account_linkage_cannot_be_faked_by_temporary_oauth():
    def dishonest(sid):
        return {"authentication_temporarily_present": False,
                "account_linked": True, "owner_selection_required": False}
    with pytest.raises(ValueError):
        connection_status_projection(sid=SID, key_reader=_key_rows, public_reader=dishonest)


def test_exact_authenticated_status_route_never_calls_external_provider():
    gate = {"owner": False}
    calls = []
    def key_reader(sid):
        calls.append("key_status")
        return _key_rows(sid)
    def public_reader(sid):
        calls.append("public_status")
        return _public(sid)
    app = Flask(__name__)
    app.secret_key = "synthetic-session-only"
    app.register_blueprint(create_connection_truth_blueprint(
        owner_authorize=lambda: gate["owner"],
        key_reader=key_reader, public_reader=public_reader,
    ))
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["tower_session_id"] = SID
    assert client.get(PATH).status_code == 403
    assert calls == []
    gate["owner"] = True
    response = client.get(PATH)
    assert response.status_code == 200
    assert calls == ["key_status", "public_status"]
    assert "no-store" in response.headers["Cache-Control"]
    assert response.headers["Vary"] == "Cookie"
    assert response.headers["Content-Security-Policy"] == "default-src 'none'"
    assert SECRET.encode() not in response.data
    assert response.get_json()["live_feed_count_verified"] is None
    assert client.post(PATH).status_code == 405


def test_source_reader_failure_is_generic_hold_not_secret_error():
    app = Flask("faulty_source")
    app.secret_key = "synthetic-session"
    app.register_blueprint(create_connection_truth_blueprint(
        owner_authorize=lambda: True,
        key_reader=lambda sid: (_ for _ in ()).throw(RuntimeError(SECRET)),
        public_reader=_public,
    ))
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["tower_session_id"] = SID
    app.testing = False
    response = client.get(PATH)
    assert response.status_code == 503
    assert SECRET.encode() not in response.data


def test_canonical_tower_routes_and_existing_dissemination_preserved():
    for path in (PATH, keys.PATH, "/ob/research/keyless.json", "/ob/data-desk/public"):
        assert path in PROTECTED_EXACT_OB_ROUTES
        policy = match_ob_guard_policy(path)
        assert policy["match_type"] == "exact"
        assert policy["policy"].get("public_allowed", False) is False
    for path in (PATH + "/connect", keys.PATH + "/export", "/ob/data-desk/nonexistent"):
        assert match_ob_guard_policy(path)["match_type"] == "unmapped_default_deny"
    app_source = (ROOT / "tower/ob_market_data_desk_integration.py").read_text()
    assert "register_public_owner_connection(app," in app_source
    assert "create_keyless_context_blueprint(" in app_source
    assert "register_provider_key_desk(app," in app_source
    assert "create_connection_truth_blueprint(" in app_source
    html = (ROOT / "web/templates/market_data_desk.html").read_text()
    assert "ob_keyless_context.js" not in html
    assert "ob_event_trace.js" in html
    assert keys.PATH in html and PATH in html
    assert "ob_connection_truth.js" in html
    nav = (ROOT / "web/static/ob/ob_nav_shell.js").read_text()
    assert 'navLink(path, "/ob/trade-center", "Trade Center"' in nav
    assert 'navLink(path, "/ob/review-center", "Review Center"' in nav
    assert 'TOWER_RETURN_PATH = "/tower/return/observatory"' in nav


def test_duplicate_credential_form_fields_are_denied(monkeypatch):
    monkeypatch.setenv("OB_PROVIDER_KEY_DESK_ENABLED", "1")
    monkeypatch.setattr(keys, "_approved_browser_origin", lambda: "https://tower.example")
    memory = keys.TemporaryProviderKeyStore()
    app = Flask("duplicate_key_form", template_folder=str(ROOT / "web/templates"))
    app.secret_key = "fictional-only"
    app.register_blueprint(keys.create_provider_key_blueprint(
        owner_authorize=lambda: True, store=memory,
        probe=lambda *_: "READ_ONLY_CHECK_PASSED",
    ))
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["tower_session_id"] = SID
    assert client.get(keys.PATH).status_code == 200
    with client.session_transaction() as sess:
        csrf = sess["ob_provider_key_csrf"]
    fields = MultiDict([
        ("csrf", csrf), ("provider", "finnhub"),
        ("provider", "alpha_vantage"), ("operation", "save"),
        ("secret", SECRET),
    ])
    response = client.post(keys.PATH, data=fields, headers={
        "Origin": "https://tower.example", "Sec-Fetch-Site": "same-origin",
    })
    assert response.status_code == 403
    assert memory.get(SID, "finnhub") is None
    assert memory.get(SID, "alpha_vantage") is None
    assert SECRET.encode() not in response.data
