"""OBSIM076–085: read-only status/sample/final evidence cannot escape /new CSRF rotation."""
from datetime import timedelta

import pytest
from flask import request

from test_obsim056_060_hosted_owner_rehearsal import (
    BASE, ORIGIN, build_app, get, post, setup_page,
)
from tower import ob_hosted_owner_rehearsal as hosted


@pytest.mark.parametrize("path", ["status.json", "sample.json", "evidence.json"])
def test_076_077_old_get_between_gate_and_view_cannot_read_new_workspace(monkeypatch, path):
    app, first, state = build_app(monkeypatch)
    old_token = setup_page(first)
    state["now"] = BASE + timedelta(seconds=30)
    assert post(first, "stop", old_token).status_code == 200
    if path == "evidence.json":
        # The previous token could read valid finalized fictional evidence.
        # After a concurrent /new it must never read the successor workspace.
        assert get(first, hosted.API + path, old_token).status_code == 200

    # The same signed Tower cookie in two browser tabs, but two distinct
    # Flask test clients. Trigger the second tab's legitimate /new AFTER the
    # first tab passes the existing before_request token check and BEFORE its
    # actual GET view runs. No timing/sleep nondeterminism is needed.
    second = app.test_client()
    signed = first.get_cookie("session", domain="tower-owner.example")
    assert signed is not None
    second.set_cookie(
        "session", signed.value, domain="tower-owner.example", secure=True,
    )
    moment = {"armed": True, "token": None}

    def rotate_during_first_read():
        if request.path != hosted.API + path or not moment["armed"]:
            return None
        moment["armed"] = False
        new = post(second, "new", old_token)
        assert new.status_code == 200, new.get_data(as_text=True)
        moment["token"] = new.json["new_rehearsal_token"]
        return None

    # Test-only injection AFTER first dispatch: Flask intentionally rejects
    # public decorator registration after a request has already been served.
    # The app is isolated; append directly to its callback list to produce the
    # deterministic between-gate-and-view race, not a production route change.
    app.before_request_funcs.setdefault(None, []).append(rotate_during_first_read)

    stale = get(first, hosted.API + path, old_token)
    assert stale.status_code == 409, stale.get_data(as_text=True)
    assert moment["token"] and moment["token"] != old_token
    # Newly rotated session is active and has no finalized export yet.
    expected_new = 409 if path == "evidence.json" else 200
    assert get(first, hosted.API + path, moment["token"]).status_code == expected_new
    assert get(first, hosted.API + "status.json", moment["token"]).json["accepted_ticks"] == 0
    assert get(first, hosted.API + "status.json", old_token).status_code == 403


def test_078_unrecognized_read_token_and_missing_workspace_stay_denied(monkeypatch):
    _, client, state = build_app(monkeypatch)
    token = setup_page(client)
    for path in ("status.json", "sample.json", "evidence.json"):
        assert get(client, hosted.API + path, "invented-token").status_code == 403
    with client.session_transaction(base_url=ORIGIN) as s:
        s["tower-session"] = "changed-session"
    for path in ("status.json", "sample.json", "evidence.json"):
        assert get(client, hosted.API + path, token).status_code == 409


def test_079_feature_off_routes_never_promote_or_create_workspace(monkeypatch):
    app, client, _ = build_app(monkeypatch, enabled=False)
    assert get(client, hosted.ENTRY).status_code == 503
    for path in ("status.json", "sample.json", "evidence.json"):
        assert get(client, hosted.API + path).status_code == 503
    flags = app.extensions["ob_hosted_owner_rehearsal_registered"]
    assert flags["enabled"] is False
    assert flags["manual_live_grant"] is False
    assert flags["durable_archive"] is False


def test_080_no_new_production_permission_or_hosting_from_read_hardening():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    source = (root / "tower/ob_hosted_owner_rehearsal.py").read_text()
    assert "def _current_read_item():" in source
    assert "workspaces.get(key) is item" in source
    assert "secrets.compare_digest(" in source
    assert "with lock:\n            item = _current_read_item()" in source
    assert "with lock:\n            _current_read_item()" in source
    assert 'def evidence():\n        with lock:' in source
    assert 'enabled = os.environ.get("OB_OWNER_REHEARSAL_HOSTED_ENABLED") == "1"' in source
    assert '"durable_archive": False' in source
    assert '"manual_live_unlock": False' in source
    assert '"broker_submission": False' in source
    assert '"capital_movement": False' in source
