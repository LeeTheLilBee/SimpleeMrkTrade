"""Runtime regression: legacy OB guard must read owner identity from signed Tower session.

A route's critical/view policy alone is not proof of owner identity. PACK046's
old legacy session/query extractor runs before hosted Tower's HTTP gate, and
previously classified a legitimate Tower login as an ordinary internal user.
"""
from datetime import datetime, timedelta, timezone

from flask import Flask, request, session
import pytest

from tower.ob_route_guard import (
    build_locked_ob_response, evaluate_ob_request_guard, should_block_ob_request,
)
import tower.ob_web_route_enforcement as web_guard

DESK = ("/ob/data-desk", "/ob/data-desk/public")


def _tower_owner(session):
    session["tower_authenticated"] = True
    session["tower_role"] = "owner"
    session["owner_id"] = "fixture_owner_nonlegacy_identifier"


@pytest.mark.parametrize("path", DESK)
def test_actual_tower_owner_session_supplies_critical_view_without_legacy_aliases(path):
    app = Flask(__name__)
    app.secret_key = "synthetic-only"
    with app.test_request_context(path + "?ob_role=beta&ob_clearance=public"):
        _tower_owner(session)
        # Runtime legacy extractor may pass none or user-controlled query hints.
        for role, clearance in (("", ""), ("beta", "internal"), ("owner", "public")):
            result = evaluate_ob_request_guard(
                path=path, user_id="browser_supplied_user",
                role=role, user_clearance_level=clearance,
            )
            assert result["allowed"] is True, result
            assert result["metadata"]["user_id"] == "fixture_owner_nonlegacy_identifier"
            assert result["metadata"]["role"] == "owner"
            assert result["metadata"]["user_clearance_level"] == "critical"
            assert result["metadata"]["required_clearance_level"] == "critical"


@pytest.mark.parametrize("path", DESK)
def test_url_claims_and_legacy_role_do_not_mint_owner_clearance_without_tower_session(path):
    app = Flask(__name__)
    app.secret_key = "synthetic-only"
    with app.test_request_context(path + "?ob_user_id=owner_solice&ob_role=owner&ob_clearance=critical"):
        result = evaluate_ob_request_guard(
            path=path, user_id="owner_solice",
            role="owner", user_clearance_level="critical",
        )
        assert result["allowed"] is False
        assert result["reason_code"] == "ob_clearance_level_too_low"
        assert result["metadata"]["user_id"] == "anonymous"
        session.update(tower_authenticated=True, tower_role="admin",
                       owner_id="fixture_nonowner")
        result = evaluate_ob_request_guard(
            path=path, user_id="owner_solice",
            role="owner", user_clearance_level="critical",
        )
        assert result["allowed"] is False
        assert result["metadata"]["user_clearance_level"] == "internal"


@pytest.fixture
def app(monkeypatch):
    app = Flask(__name__)
    app.secret_key = "synthetic-only"
    app.config["TESTING"] = True

    # Model the real order: historical PACK046 guard is installed first and
    # consumes its old, untrusted identity aliases; real Tower HTTP gate next.
    @app.before_request
    def legacy_guard():
        if request.path not in DESK and not request.path.startswith("/ob/"):
            return None
        decision = should_block_ob_request(
            path=request.path,
            user_id=request.args.get("ob_user_id", session.get("username", "anonymous")),
            role=request.args.get("ob_role", session.get("role", "")),
            user_clearance_level=request.args.get("ob_clearance", session.get("clearance_level", "")),
        )
        if decision["block"]:
            return build_locked_ob_response(
                reason_code=decision["reason_code"],
                human_reason=decision["human_reason"],
                path=request.path,
                decision=decision,
            )
        return None

    monkeypatch.setattr(web_guard, "operational_ob_access_active", lambda: True)
    web_guard.register_ob_protected_route_enforcement(app)

    for path in DESK:
        app.add_url_rule(path, endpoint=path, view_func=lambda: "owner-only-source-view")
    return app


@pytest.mark.parametrize("path", DESK)
def test_runtime_owner_navigation_then_independent_step_up_and_denied_spoof(app, path):
    client = app.test_client()
    spoof = "?ob_user_id=owner_solice&ob_role=owner&ob_clearance=critical"
    assert client.get(path + spoof).status_code == 403
    with client.session_transaction() as signed:
        _tower_owner(signed)
    # Real Tower login now establishes clearance; an expired or absent step-up
    # redirects through Tower, not a false "clearance too low" page.
    expired = client.get(path + "?ob_role=beta&ob_clearance=internal")
    assert expired.status_code == 302
    assert expired.location == (
        "/tower/step-up/observatory?next="
        + path.replace("/", "%2F")
    )
    with client.session_transaction() as signed:
        signed["tower_step_up_until"] = (datetime.now(timezone.utc) +
                                         timedelta(minutes=5)).isoformat()
    allowed = client.get(path + "?ob_role=beta&ob_clearance=internal")
    assert allowed.status_code == 200
    assert allowed.get_data(as_text=True) == "owner-only-source-view"
    # An unrelated private corridor remains unmapped.
    assert client.get(path + "/other").status_code == 403


def test_standalone_clearance_catalog_remains_usable_without_http_context():
    owner = evaluate_ob_request_guard(path="/ob/data-desk/public",
                                      user_id="owner-test", role="owner")
    assert owner["allowed"] is True
    denied = evaluate_ob_request_guard(path="/ob/data-desk/public",
                                       user_id="visitor", role="viewer")
    assert denied["reason_code"] == "ob_clearance_level_too_low"
