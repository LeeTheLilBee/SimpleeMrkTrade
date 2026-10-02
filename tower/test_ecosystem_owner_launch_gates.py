from __future__ import annotations

from datetime import timedelta
from flask import Blueprint, Flask, session
import pytest

import tower.ecosystem_owner_launch_gates as gates
from tower.app_registry import route_by_path, registered_apps
from tower.ecosystem_direct_route_guard import ACCESS_RECEIPT_KEYS
from tower.tower_human_login_ob_launch import (
    SESSION_AUTHENTICATED, SESSION_ID, SESSION_OWNER_ID, SESSION_ROLE,
    SESSION_STEP_UP_UNTIL, SESSION_USERNAME, utc_now,
)


def make_app():
    app = Flask(__name__)
    app.config.update(TESTING=True, SECRET_KEY="test-only-secret-key")
    login = Blueprint("tower_human_login", __name__)
    def login_view():
        return "login"
    login.add_url_rule("/tower/login", endpoint="login", view_func=login_view, methods=["GET"])
    app.register_blueprint(login)
    gates.register_ecosystem_owner_launch_gates(app)
    return app


def owner(client, *, step_up=True):
    with client.session_transaction() as s:
        s[SESSION_AUTHENTICATED] = True
        s[SESSION_ROLE] = "owner"
        s[SESSION_OWNER_ID] = "owner_fixture"
        s[SESSION_USERNAME] = "owner"
        s[SESSION_ID] = "tower_session_" + "a" * 32
        if step_up:
            s[SESSION_STEP_UP_UNTIL] = (utc_now() + timedelta(minutes=10)).isoformat()


def test_registry_has_exact_tower_launch_routes_without_claiming_product_release():
    apps = {row["app_id"]: row for row in registered_apps()}
    assert apps["grounds"]["tower_launch_route"] == "/tower/launch/grounds"
    assert apps["buybox"]["tower_launch_route"] == "/tower/launch/buybox"
    assert apps["grounds"]["app_status"] == "registered_future_room"
    assert apps["buybox"]["app_status"] == "registered_future_room"
    assert apps["grounds"]["broker_execution_enabled"] is False
    assert apps["buybox"]["capital_action_enabled"] is False
    grounds_route = route_by_path("/tower/launch/grounds")
    buybox_route = route_by_path("/tower/launch/buybox")
    assert grounds_route["owner_only"] is True and grounds_route["requires_step_up"] is True
    assert buybox_route["owner_only"] is True and buybox_route["requires_step_up"] is True


def test_anonymous_launch_requires_tower_owner_login():
    app = make_app()
    client = app.test_client()
    response = client.get("/tower/launch/grounds")
    assert response.status_code == 302
    assert "/tower/login" in response.location


def test_owner_without_stepup_is_sent_to_shared_ecosystem_stepup():
    app = make_app()
    client = app.test_client()
    owner(client, step_up=False)
    for path, app_id in (
        ("/tower/launch/grounds", "grounds"),
        ("/tower/launch/buybox", "buybox"),
    ):
        response = client.get(path)
        assert response.status_code == 302
        assert response.location.endswith("/tower/step-up/ecosystem?app=" + app_id)


def test_ground_preflight_requires_truth_mount_receiver_and_release(monkeypatch):
    app = make_app()
    monkeypatch.setattr(gates, "_grounds_runtime_health",
                        lambda: (False, ["GROUNDS_RUNTIME_RECEIVER_NOT_CERTIFIED"]))
    blocked = gates.inspect_grounds_launch(app, truth={"launchable": False})
    assert blocked["can_launch"] is False
    assert "GROUNDS_PUBLICATION_ENTITLEMENT_OR_HEALTH_NOT_VERIFIED" in blocked["reason_codes"]
    assert "GROUNDS_SAME_ORIGIN_RUNTIME_NOT_MOUNTED" in blocked["reason_codes"]
    assert "GROUNDS_RUNTIME_RECEIVER_NOT_CERTIFIED" in blocked["reason_codes"]

    @app.get("/grounds")
    def grounds():
        return "grounds"

    # A stray or placeholder route is not the reviewed Tower<->Grounds mount.
    monkeypatch.setattr(gates, "_grounds_runtime_health", lambda: (True, []))
    route_only = gates.inspect_grounds_launch(app, truth={"launchable": True})
    assert route_only["can_launch"] is False
    assert "GROUNDS_SAME_ORIGIN_RUNTIME_NOT_MOUNTED" in route_only["reason_codes"]

    app.extensions["tower_grounds_same_origin_mount_v1"] = {
        "configured": True,
        "mounted": True,
        "same_origin": True,
        "root_path": "/grounds",
        "owner_crossing_only": True,
        "resident_staff_launch_created": False,
        "new_entitlement_granted": False,
    }
    ready = gates.inspect_grounds_launch(app, truth={"launchable": True})
    assert ready["can_launch"] is True
    assert ready["target_path"] == "/grounds"
    assert ready["broker_submission_authorized"] is False
    assert ready["capital_movement_authorized"] is False


def test_ground_launch_writes_receipt_only_after_all_gates(monkeypatch):
    app = make_app()
    @app.get("/grounds")
    def grounds():
        return "grounds"
    monkeypatch.setattr(gates, "inspect_grounds_launch", lambda _app: {
        "can_launch": True, "reason_codes": [], "state": "READY_TO_LAUNCH"
    })
    client = app.test_client()
    owner(client)
    response = client.get("/tower/launch/grounds")
    assert response.status_code == 302
    assert response.location.endswith("/grounds")
    with client.session_transaction() as s:
        receipt = s[ACCESS_RECEIPT_KEYS["grounds"]]
        assert receipt["app_id"] == "grounds"
        assert receipt["allowed"] is True
        assert receipt["new_entitlement_granted"] is False
        assert receipt["dangerous_action_unlocked"] is False


def test_blocked_ground_launch_never_writes_access_receipt(monkeypatch):
    app = make_app()
    monkeypatch.setattr(gates, "inspect_grounds_launch", lambda _app: {
        "can_launch": False, "reason_codes": ["BLOCKED_TEST"], "state": "BLOCKED"
    })
    client = app.test_client()
    owner(client)
    response = client.get("/tower/launch/grounds")
    assert response.status_code == 503
    with client.session_transaction() as s:
        assert ACCESS_RECEIPT_KEYS["grounds"] not in s


def test_buybox_bootstrap_requires_exact_https_origin_and_current_issue_preflight(monkeypatch):
    app = make_app()
    client = app.test_client()
    owner(client)
    monkeypatch.setattr(gates, "inspect_current_buybox_issue_preflight",
        lambda **_kwargs: {
            "can_issue_handoff": True, "reason_codes": [], "state": "READY_TO_ISSUE"
        })
    with client.session_transaction() as stored:
        snapshot = dict(stored)

    monkeypatch.delenv("BUYBOX_PUBLIC_ORIGIN", raising=False)
    with app.test_request_context("/tower/launch/buybox"):
        session.update(snapshot)
        missing = gates.inspect_buybox_launch(truth={"launchable": True})
    assert missing["can_launch"] is False
    assert "BUYBOX_PUBLIC_ORIGIN_NOT_CONFIGURED" in missing["reason_codes"]

    monkeypatch.setenv("BUYBOX_PUBLIC_ORIGIN", "http://buybox.example.invalid")
    with app.test_request_context("/tower/launch/buybox"):
        session.update(snapshot)
        invalid = gates.inspect_buybox_launch(truth={"launchable": True})
    assert invalid["can_launch"] is False
    assert "BUYBOX_PUBLIC_ORIGIN_INVALID" in invalid["reason_codes"]

    monkeypatch.setenv("BUYBOX_PUBLIC_ORIGIN", "https://buybox.example.invalid")
    with app.test_request_context("/tower/launch/buybox"):
        session.update(snapshot)
        ready = gates.inspect_buybox_launch(truth={"launchable": True})
    assert ready["can_launch"] is True
    assert ready["browser_bootstrap_transport_ready"] is True
    assert ready["receiver_contract"] == "POST /tower/bootstrap -> POST /tower/owner-exchange"
    assert ready["broker_submission_authorized"] is False
    assert ready["capital_movement_authorized"] is False


def test_buybox_launch_issues_post_body_only_bootstrap_after_all_gates(monkeypatch):
    app = make_app()
    client = app.test_client()
    owner(client)
    monkeypatch.setenv("BUYBOX_PUBLIC_ORIGIN", "https://buybox.example.invalid")
    monkeypatch.setattr(gates, "inspect_buybox_launch", lambda: {
        "can_launch": True, "reason_codes": [], "state": "READY_TO_LAUNCH"
    })
    monkeypatch.setattr(gates, "issue_buybox_owner_handoff", lambda **_kwargs: {
        "token": "tbh1.payload.signature",
        "broker_submission_authorized": False,
        "capital_movement_authorized": False,
        "closing_authorized": False,
        "vault_access_authorized": False,
    })
    response = client.get("/tower/launch/buybox")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'method="post"' in html
    assert 'action="https://buybox.example.invalid/tower/bootstrap"' in html
    assert 'name="handoff" value="tbh1.payload.signature"' in html
    assert "handoff=" not in html
    assert response.location is None
    assert "no-store" in response.headers["Cache-Control"]
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "form-action https://buybox.example.invalid" in response.headers["Content-Security-Policy"]
    assert "/static/tower/buybox_bootstrap_launch.js" in html
    with client.session_transaction() as s:
        assert ACCESS_RECEIPT_KEYS["buybox"] not in s


def test_buybox_launch_sanitizes_issuance_failure(monkeypatch):
    app = make_app()
    client = app.test_client()
    owner(client)
    monkeypatch.setenv("BUYBOX_PUBLIC_ORIGIN", "https://buybox.example.invalid")
    monkeypatch.setattr(gates, "inspect_buybox_launch", lambda: {
        "can_launch": True, "reason_codes": [], "state": "READY_TO_LAUNCH"
    })
    def fail(**_kwargs):
        raise gates.TowerBuyBoxIssuerUnavailable("private signer detail")
    monkeypatch.setattr(gates, "issue_buybox_owner_handoff", fail)
    response = client.get("/tower/launch/buybox")
    assert response.status_code == 503
    assert b"BUYBOX_HANDOFF_ISSUANCE_FAILED" in response.data
    assert b"private signer detail" not in response.data


def test_status_requires_current_stepup_even_for_authenticated_owner():
    app = make_app()
    client = app.test_client()
    owner(client, step_up=False)
    for path in ("/tower/launch/grounds.json", "/tower/launch/buybox.json"):
        response = client.get(path)
        assert response.status_code == 403
        payload = response.get_json()
        assert payload["can_launch"] is False
        assert "CURRENT_TOWER_OWNER_STEP_UP_REQUIRED" in payload["reason_codes"]


def test_shared_stepup_accepts_only_reviewed_apps_and_uses_owner_password(monkeypatch):
    app = make_app()
    client = app.test_client()
    owner(client, step_up=False)
    assert client.get("/tower/step-up/ecosystem?app=vault").status_code == 404

    monkeypatch.setattr(gates, "verify_owner_credentials",
                        lambda *, username, password: username == "owner" and password == "correct")
    response = client.post("/tower/step-up/ecosystem",
                           data={"app": "grounds", "password": "correct"})
    assert response.status_code == 302
    assert response.location.endswith("/tower/launch/grounds")
    with client.session_transaction() as s:
        assert SESSION_STEP_UP_UNTIL in s


def test_unknown_product_launch_routes_remain_unregistered():
    app = make_app()
    rules = {r.rule for r in app.url_map.iter_rules()}
    assert "/tower/launch/vault" not in rules
    assert "/tower/launch/simplee-on-the-go" not in rules
    assert "/tower/launch/grounds" in rules
    assert "/tower/launch/buybox" in rules
