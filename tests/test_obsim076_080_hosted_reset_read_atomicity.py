"""OBSIM076–080: deterministic read-after-reset race, no stale owner token leak."""
from __future__ import annotations

from datetime import timedelta
import inspect
from pathlib import Path

import pytest
from flask import request

from test_obsim056_060_hosted_owner_rehearsal import (
    BASE, SAMPLE, build_app, get, post, setup_page,
)
from tower import ob_hosted_owner_rehearsal as hosted

ROOT = Path(__file__).resolve().parents[1]


def inject_rotation_after_access_gate(app, state, *, request_path):
    """Simulate a separately authorized /new between gate and view.

    Flask runs before_request callbacks in registration order. The production
    gate validates old token first. This test hook swaps its process-local
    workspace just after that check; the view must independently recheck.
    No public production hook is added.
    """
    gate = next(
        callback for callback in app.before_request_funcs[None]
        if callback.__name__ == "_hosted_owner_rehearsal_gate"
    )
    captured = inspect.getclosurevars(gate).nonlocals
    workspaces = captured["workspaces"]
    lock = captured["lock"]
    fired = []

    @app.before_request
    def _test_interleave_authorized_rotation():
        if request.path == request_path and not fired:
            with lock:
                assert len(workspaces) == 1
                key = next(iter(workspaces))
                old = workspaces[key]
                assert old.desk.session.status.value == "RUNNING"
                new = hosted._Workspace(state["now"])
                assert old.csrf != new.csrf
                workspaces[key] = new
                fired.append((old, new))
    return fired


@pytest.mark.parametrize("endpoint", ("status.json", "sample.json"))
def test_076_077_old_token_never_reads_new_workspace_after_gate_reset(monkeypatch, endpoint):
    app, client, state = build_app(monkeypatch)
    old = setup_page(client)
    fired = inject_rotation_after_access_gate(
        app, state, request_path=hosted.API + endpoint,
    )
    stale = get(client, hosted.API + endpoint, old)
    assert len(fired) == 1
    assert stale.status_code == 409
    assert stale.json["status"] == "REHEARSAL_SESSION_ROTATED_REENTER_TOWER"
    assert stale.json["manual_live_unlock"] is False
    assert stale.json["broker_submission"] is False
    assert "new_rehearsal_token" not in stale.json
    assert "last_lanes" not in stale.json
    assert "account_key" not in stale.get_data(as_text=True)
    assert get(client, hosted.API + endpoint, old).status_code == 403
    current = setup_page(client)
    assert current == fired[0][1].csrf and current != old
    assert get(client, hosted.API + endpoint, current).status_code == 200


@pytest.mark.parametrize("endpoint", ("status.json", "sample.json"))
def test_078_079_owner_revoked_after_initial_gate_cannot_read(monkeypatch, endpoint):
    app, client, state = build_app(monkeypatch)
    token = setup_page(client)

    @app.before_request
    def _test_authority_lost_after_gate():
        if request.path == hosted.API + endpoint:
            state["access"] = False

    denied = get(client, hosted.API + endpoint, token)
    assert denied.status_code != 200
    assert "new_rehearsal_token" not in denied.get_data(as_text=True)


def test_080_new_session_manual_tick_retains_strict_source_and_no_live_grant(monkeypatch):
    app, client, state = build_app(monkeypatch)
    old = setup_page(client)
    state["now"] = BASE + timedelta(seconds=30)
    assert post(client, "tick", old, SAMPLE).status_code == 200
    assert post(client, "stop", old).status_code == 200
    renewed = post(client, "new", old)
    assert renewed.status_code == 200
    current = renewed.json["new_rehearsal_token"]
    assert current != old
    assert get(client, hosted.API + "status.json", old).status_code == 403
    status = get(client, hosted.API + "status.json", current)
    assert status.status_code == 200 and status.json["accepted_ticks"] == 0
    assert status.json["durable_archive"] is False
    assert status.json["source_provider_authenticated"] is False
    assert status.json["manual_live_unlock"] is False
    assert status.json["capital_movement"] is False
    # No old source input may masquerade as a new live/trading permission.
    assert post(client, "tick", old, SAMPLE).status_code == 403
    assert post(client, "tick", current, {**SAMPLE, "source_kind": "LIVE_OBSERVED"}).status_code == 409
    source = (ROOT / "tower/ob_hosted_owner_rehearsal.py").read_text()
    assert "def read_checked_workspace():" in source
    assert "def read_rotated():" in source
    assert "return jsonify(view(item, clock()))" in source
    assert source.count("if read_checked_workspace() is None:") == 1
    assert source.count("item = read_checked_workspace()") == 1
