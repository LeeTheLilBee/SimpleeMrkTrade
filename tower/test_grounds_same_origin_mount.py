from __future__ import annotations

from datetime import timedelta
import json
from types import SimpleNamespace

from flask import Blueprint, Flask

import tower.ecosystem_owner_launch_gates as gates
import tower.grounds_same_origin_mount as mount
from tower.ecosystem_direct_route_guard import (
    ACCESS_RECEIPT_KEYS, register_ecosystem_direct_route_guard,
)
from tower.tower_human_login_ob_launch import (
    SESSION_AUTHENTICATED, SESSION_ID, SESSION_OWNER_ID, SESSION_ROLE,
    SESSION_STEP_UP_UNTIL, SESSION_USERNAME, utc_now,
)


def fake_ground_app(environ, start_response):
    payload=json.dumps({
        "path":environ.get("PATH_INFO"),
        "method":environ.get("REQUEST_METHOD"),
        "query":environ.get("QUERY_STRING"),
    }).encode("utf-8")
    start_response("200 OK",[
        ("Content-Type","application/json"),
        ("Content-Length",str(len(payload))),
        ("Cache-Control","no-store"),
    ])
    return [payload]


def owner(client):
    with client.session_transaction() as s:
        s[SESSION_AUTHENTICATED]=True
        s[SESSION_ROLE]="owner"
        s[SESSION_OWNER_ID]="owner_fixture"
        s[SESSION_USERNAME]="owner"
        s[SESSION_ID]="tower_session_"+"g"*32
        s[SESSION_STEP_UP_UNTIL]=(utc_now()+timedelta(minutes=10)).isoformat()


def test_mount_disabled_registers_no_product_route(monkeypatch):
    monkeypatch.delenv(mount.ENABLE_ENV,raising=False)
    app=Flask(__name__)
    mount.register_configured_grounds_same_origin_runtime(app)
    assert "/grounds" not in {r.rule for r in app.url_map.iter_rules()}
    status=app.extensions[mount.EXTENSION_KEY]
    assert status["mounted"] is False
    assert status["reason_code"]=="GROUNDS_SAME_ORIGIN_MOUNT_NOT_CONFIGURED"


def test_opt_in_without_real_ground_factory_fails_closed_and_sanitized(monkeypatch):
    monkeypatch.setenv(mount.ENABLE_ENV,"1")
    monkeypatch.setattr(mount,"import_module",lambda _name: (_ for _ in ()).throw(
        RuntimeError("private module diagnostic")
    ))
    app=Flask(__name__)
    mount.register_configured_grounds_same_origin_runtime(app)
    assert "/grounds" not in {r.rule for r in app.url_map.iter_rules()}
    assert app.extensions[mount.EXTENSION_KEY]["reason_code"]=="GROUNDS_PRODUCTION_FACTORY_UNAVAILABLE"
    assert "private" not in str(app.extensions[mount.EXTENSION_KEY])


def test_ground_factory_failure_does_not_break_tower_or_register_route(monkeypatch):
    monkeypatch.setenv(mount.ENABLE_ENV,"1")
    production=SimpleNamespace(
        create_wsgi_application=lambda: (_ for _ in ()).throw(
            RuntimeError("postgresql://secret.invalid/grounds")
        )
    )
    monkeypatch.setattr(mount,"import_module",lambda _name: production)
    app=Flask(__name__)
    mount.register_configured_grounds_same_origin_runtime(app)
    assert "/grounds" not in {r.rule for r in app.url_map.iter_rules()}
    assert app.extensions[mount.EXTENSION_KEY]["reason_code"]=="GROUNDS_PRODUCTION_PREFLIGHT_BLOCKED"


def test_real_child_wsgi_receives_original_ground_prefix(monkeypatch):
    monkeypatch.setenv(mount.ENABLE_ENV,"1")
    monkeypatch.setattr(mount,"import_module",lambda _name: SimpleNamespace(
        create_wsgi_application=lambda: fake_ground_app,
    ))
    app=Flask(__name__)
    app.config.update(TESTING=True,SECRET_KEY="fixture-secret")
    mount.register_configured_grounds_same_origin_runtime(app)
    client=app.test_client()
    root=client.get("/grounds?view=owner")
    assert root.status_code==200
    assert root.get_json()=={"path":"/grounds","method":"GET","query":"view=owner"}
    nested=client.post("/grounds/api/work?x=1")
    assert nested.status_code==200
    assert nested.get_json()=={"path":"/grounds/api/work","method":"POST","query":"x=1"}
    status=app.extensions[mount.EXTENSION_KEY]
    assert status["mounted"] is True
    assert status["resident_staff_launch_created"] is False


def test_owner_launch_crosses_only_after_mount_and_existing_tower_receipt_guard(monkeypatch):
    monkeypatch.setenv(mount.ENABLE_ENV,"1")
    monkeypatch.setattr(mount,"import_module",lambda _name: SimpleNamespace(
        create_wsgi_application=lambda: fake_ground_app,
    ))
    app=Flask(__name__)
    app.config.update(TESTING=True,SECRET_KEY="fixture-secret")
    login=Blueprint("tower_human_login",__name__)
    login.add_url_rule("/tower/login",endpoint="login",view_func=lambda:"login",methods=["GET"])
    app.register_blueprint(login)

    # Mount first, then preserve Tower's generic direct-route receipt guard.
    mount.register_configured_grounds_same_origin_runtime(app)
    register_ecosystem_direct_route_guard(app)
    gates.register_ecosystem_owner_launch_gates(app)
    monkeypatch.setattr(gates,"app_truth_by_id",lambda app_id:{"launchable":app_id=="grounds"})
    monkeypatch.setattr(gates,"_grounds_runtime_health",lambda:(True,[]))

    client=app.test_client()
    owner(client)
    direct=client.get("/grounds")
    assert direct.status_code==503
    launch=client.get("/tower/launch/grounds",follow_redirects=False)
    assert launch.status_code==302
    assert launch.location.endswith("/grounds")
    with client.session_transaction() as s:
        assert s[ACCESS_RECEIPT_KEYS["grounds"]]["app_id"]=="grounds"
    crossed=client.get("/grounds")
    assert crossed.status_code==200
    assert crossed.get_json()["path"]=="/grounds"


def test_launch_preflight_stays_blocked_when_mount_factory_is_not_ready(monkeypatch):
    monkeypatch.setenv(mount.ENABLE_ENV,"1")
    monkeypatch.setattr(mount,"import_module",lambda _name: SimpleNamespace(
        create_wsgi_application=lambda: (_ for _ in ()).throw(RuntimeError("blocked")),
    ))
    app=Flask(__name__)
    app.config.update(TESTING=True,SECRET_KEY="fixture-secret")
    mount.register_configured_grounds_same_origin_runtime(app)
    monkeypatch.setattr(gates,"_grounds_runtime_health",lambda:(True,[]))
    report=gates.inspect_grounds_launch(app,truth={"launchable":True})
    assert report["can_launch"] is False
    assert "GROUNDS_SAME_ORIGIN_RUNTIME_NOT_MOUNTED" in report["reason_codes"]
