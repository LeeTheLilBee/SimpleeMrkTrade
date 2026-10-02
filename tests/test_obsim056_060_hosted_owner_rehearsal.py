"""OBSIM056–060: real HTTP negative and active synthetic owner Tower adapter tests."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re

from flask import Flask, session
import pytest

from tower import ob_hosted_owner_rehearsal as hosted
from tower import ob_web_route_enforcement as gate
from web.ob_multi_simulation_harness import stable_hash

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://tower-owner.example"
BASE = datetime(2026, 9, 26, 12, tzinfo=timezone.utc)
SAMPLE = json.loads((ROOT / "examples/obsim_owner_synthetic_hold_example.json").read_text())


def build_app(monkeypatch, *, enabled=True, authorized=True, stepped=True, access=True):
    state = {"owner": authorized, "step": stepped, "access": access, "now": BASE}
    monkeypatch.setattr(gate, "owner_session_active", lambda: state["owner"])
    monkeypatch.setattr(gate, "step_up_active", lambda: state["step"])
    monkeypatch.setattr(gate, "operational_ob_access_active", lambda: state["access"])
    monkeypatch.setattr(hosted, "owner_session_active", lambda: state["owner"])
    monkeypatch.setattr(hosted, "step_up_active", lambda: state["step"])
    monkeypatch.setattr(hosted, "operational_ob_access_active", lambda: state["access"])
    monkeypatch.setattr(hosted, "ensure_tower_session_id", lambda: session.get("tower-session", ""))

    app = Flask(
        __name__, template_folder=str(ROOT / "web/templates"),
        static_folder=str(ROOT / "web/static"), static_url_path="/static",
    )
    app.secret_key = "synthetic-test-only"
    app.testing = True

    @app.get("/tower/login")
    def login():
        return "LOGIN"

    @app.get("/tower/access-home")
    def access_home():
        return "HOME"

    @app.get("/tower/launch/observatory")
    def launch():
        return "LAUNCH"

    @app.get("/ob/owner-dashboard")
    def dashboard():
        from flask import render_template
        return render_template("owner_dashboard.html")

    gate.register_ob_protected_route_enforcement(app)
    hosted.register_ob_hosted_owner_rehearsal(
        app, enabled=enabled,
        canonical_origin=ORIGIN if enabled else "",
        clock=lambda: state["now"],
    )
    client = app.test_client()
    with client.session_transaction(base_url=ORIGIN) as cookie:
        cookie["tower-session"] = "tower-session-" + "b" * 36
        cookie[hosted.SESSION_OWNER_ID] = "owner-test-1"
    return app, client, state


def get(client, path, token=None, origin=ORIGIN):
    return client.get(
        path, base_url=origin,
        headers={} if token is None else {"X-OB-Rehearsal-Token": token},
        follow_redirects=False,
    )


def setup_page(client):
    response = get(client, hosted.ENTRY)
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    match = re.search(r'data-ob-csrf="([^"]+)"', text)
    assert match is not None
    assert "VOLATILE REPORT ONLY" in text
    assert "TOWER PROTECTED OWNER" in text
    assert "Restart or deployment loses this session" in text
    assert "ob_hosted_owner_rehearsal.js" in text
    return match.group(1)


def post(client, path, token, data=None, origin=ORIGIN, override=None):
    headers = {"X-OB-Rehearsal-Token": token, "Origin": origin}
    if override:
        headers.update(override)
    return client.post(
        hosted.API + path + ".json", base_url=origin, headers=headers,
        data=json.dumps({} if data is None else data),
        content_type="application/json",
        follow_redirects=False,
    )


def test_056_default_disabled_and_exact_security_registry(monkeypatch):
    _, client, _ = build_app(monkeypatch, enabled=False)
    assert get(client, hosted.ENTRY).status_code == 503
    assert get(client, hosted.API + "status.json").status_code == 503
    assert gate.is_approved_ob_web_room(hosted.ENTRY)
    for name in hosted.METHODS:
        assert gate.is_approved_ob_web_room(hosted.API + name)
    for path in (
        "/ob/owner-rehearsal/random", "/ob/owner-rehearsal/status.json/more",
        "/ob/owner-rehearsal/fills.json", "/ob/owner-rehearsal-trade",
    ):
        assert not gate.is_approved_ob_web_room(path)
        assert get(client, path).status_code == 403
    assert not gate.is_owner_only_ob_web_room(hosted.ENTRY)  # requires step-up AND OB receipt
    for bad in ("http://tower-owner.example", "https://evil.example/path", "https://a@host.example", ""):
        with pytest.raises(ValueError):
            hosted._origin(bad)


def test_057_cannot_enter_on_missing_owner_step_up_or_operational_receipt(monkeypatch):
    _, client, state = build_app(monkeypatch)
    state["owner"] = False
    location = get(client, hosted.ENTRY).headers["Location"]
    assert "/tower/login?" in location
    assert "next=%2Fob%2Fowner-rehearsal" in location
    state["owner"] = True
    state["step"] = False
    location = get(client, hosted.ENTRY).headers["Location"]
    assert "/tower/step-up/observatory?" in location
    assert "next=%2Fob%2Fowner-rehearsal" in location
    state["step"] = True
    state["access"] = False
    location = get(client, hosted.ENTRY).headers["Location"]
    assert "/tower/launch/observatory?" in location
    assert "next=%2Fob%2Fowner-rehearsal" in location
    state["access"] = True
    token = setup_page(client)
    state["access"] = False
    assert get(client, hosted.API + "status.json", token).status_code != 200
    assert post(client, "tick", token, SAMPLE).status_code != 200
    state["access"] = True
    state["owner"] = False
    assert get(client, hosted.API + "status.json", token).status_code != 200
    state["owner"] = True
    assert get(client, hosted.API + "status.json", token).status_code == 200


def test_058_host_origin_token_account_and_malformed_json_denied(monkeypatch):
    _, client, state = build_app(monkeypatch)
    token = setup_page(client)
    state["now"] += timedelta(seconds=30)
    assert get(client, hosted.ENTRY, origin="https://another-owner.example").status_code == 403
    assert get(client, hosted.API + "status.json").status_code == 403
    assert get(client, hosted.API + "status.json", "attacker").status_code == 403
    assert get(client, hosted.API + "status.json", token, origin="https://another-owner.example").status_code == 403
    assert post(client, "tick", token, SAMPLE, override={"Origin": "https://evil.example"}).status_code == 403
    assert post(client, "tick", "attacker", SAMPLE).status_code == 403
    assert client.post(
        hosted.API + "tick.json", base_url=ORIGIN, headers={
            "X-OB-Rehearsal-Token": token, "Origin": ORIGIN,
        }, data=json.dumps(SAMPLE), content_type="text/plain",
    ).status_code == 415
    assert client.post(
        hosted.API + "tick.json", base_url=ORIGIN, headers={
            "X-OB-Rehearsal-Token": token, "Origin": ORIGIN,
        }, data=b'{"source_kind":"SYNTHETIC","source_kind":"SYNTHETIC"}',
        content_type="application/json",
    ).status_code == 400
    assert client.post(
        hosted.API + "tick.json", base_url=ORIGIN, headers={
            "X-OB-Rehearsal-Token": token, "Origin": ORIGIN,
        }, data=b'{"x":NaN}', content_type="application/json",
    ).status_code == 400
    assert post(client, "pause", token, {"approved": True}).status_code == 400
    bad = {**SAMPLE, "account_key": "ob_acct_trust"}
    assert post(client, "tick", token, bad).status_code == 409
    spoof = {**SAMPLE, "verified_broker_account": True}
    assert post(client, "tick", token, spoof).status_code == 409
    assert get(client, hosted.API + "status.json", token).json["accepted_ticks"] == 0
    assert not hasattr(hosted, "BROKER_ORDER_API")


def test_059_real_three_lane_tick_pause_resume_final_and_new_with_token(monkeypatch):
    _, client, state = build_app(monkeypatch)
    token = setup_page(client)
    first = get(client, hosted.API + "status.json", token).json
    assert first["due"]["state"] == "WAIT_INTERVAL"
    assert first["storage_state"] == "VOLATILE_PROCESS_MEMORY_ONLY"
    assert first["durable_archive"] is False and first["restart_recovery"] is False
    assert first["manual_live_unlock"] is False and first["source_provider_authenticated"] is False
    assert post(client, "tick", token, SAMPLE).status_code == 409
    state["now"] += timedelta(seconds=30)
    a = post(client, "tick", token, SAMPLE)
    assert a.status_code == 200, a.get_data(as_text=True)
    assert a.json["accepted_ticks"] == 1
    assert len(a.json["last_lanes"]) == 3
    assert a.json["broker_submission"] is False
    state["now"] += timedelta(seconds=1)
    assert post(client, "pause", token).json["state"] == "PAUSED"
    state["now"] += timedelta(seconds=61)
    assert post(client, "tick", token, SAMPLE).status_code == 409
    assert post(client, "resume", token).json["state"] == "RUNNING"
    state["now"] += timedelta(seconds=29)
    assert post(client, "tick", token, SAMPLE).status_code == 409
    again = deepcopy(SAMPLE)
    again["frame"]["frame_id"] = "HOSTED-F002"
    again["frame"]["observed_at"] = "2026-09-24T10:01:00-04:00"
    again["frame"]["source_reference"] = "SYNTHETIC-F002-NOT-MARKET-FEED"
    for lane in again["decisions"]:
        again["decisions"][lane]["decision_id"] = "HOSTED-F002-" + lane
    state["now"] += timedelta(seconds=1)
    second = post(client, "tick", token, again)
    assert second.status_code == 200, second.get_data(as_text=True)
    assert second.json["accepted_ticks"] == 2
    stopped = post(client, "stop", token)
    assert stopped.status_code == 200
    assert stopped.json["archive_state"] == "EPHEMERAL_FINALIZED_REPORT_ONLY"
    assert stopped.json["archive_tick_count"] == 2
    assert stopped.json["durable_archive"] is False
    assert post(client, "tick", token, again).status_code == 409
    renewed = post(client, "new", token)
    assert renewed.status_code == 200
    assert renewed.json["accepted_ticks"] == 0
    assert renewed.json["state"] == "RUNNING"
    assert renewed.json["previous_token_revoked"] is True
    successor = renewed.json["new_rehearsal_token"]
    assert successor != token and len(successor) >= 32
    assert get(client, hosted.API + "status.json", token).status_code == 403
    assert get(client, hosted.API + "status.json", successor).status_code == 200
    assert "new_rehearsal_token" not in get(
        client, hosted.API + "status.json", successor
    ).json
    assert "new_rehearsal_token" not in get(
        client, hosted.API + "sample.json", successor
    ).json


def test_060_logout_session_rotation_memory_restart_and_headers(monkeypatch):
    app, client, state = build_app(monkeypatch)
    token = setup_page(client)
    page = get(client, hosted.ENTRY)
    assert page.headers["Cache-Control"] == "no-store, private"
    assert "frame-ancestors 'none'" in page.headers["Content-Security-Policy"]
    assert page.headers["Referrer-Policy"] == "no-referrer"
    with client.session_transaction(base_url=ORIGIN) as cookie:
        cookie["tower-session"] = "tower-session-rotated"
    assert get(client, hosted.API + "status.json", token).status_code == 409
    newer = setup_page(client)
    assert newer != token
    assert get(client, hosted.API + "status.json", token).status_code == 403
    # Separate process/Flask app has no in-memory archive to recover.
    app2, client2, state2 = build_app(monkeypatch)
    assert get(client2, hosted.API + "status.json", newer).status_code == 409
    fresh_token = setup_page(client2)
    assert fresh_token != newer
    assert get(client2, hosted.API + "status.json", fresh_token).json["accepted_ticks"] == 0
    js = (ROOT / "web/static/ob/ob_hosted_owner_rehearsal.js").read_text()
    assert 'credentials: "same-origin"' in js
    assert "setInterval" in js and "innerHTML" not in js
    assert "ob_local_owner_rehearsal_ui" not in (
        ROOT / "web/hosted_tower.py"
    ).read_text()
    assert "register_configured_ob_hosted_owner_rehearsal(app)" in (
        ROOT / "web/hosted_tower.py"
    ).read_text()
