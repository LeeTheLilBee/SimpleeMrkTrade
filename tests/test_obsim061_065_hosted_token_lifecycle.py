"""OBSIM061–065: reset is a new owner-local capability; old token never survives."""
from datetime import timedelta
from pathlib import Path

from test_obsim056_060_hosted_owner_rehearsal import (
    BASE, ORIGIN, SAMPLE, build_app, get, post, setup_page,
)
from tower import ob_hosted_owner_rehearsal as hosted

ROOT = Path(__file__).resolve().parents[1]


def test_061_new_token_rotates_and_old_token_cannot_observe_new_session(monkeypatch):
    _, client, state = build_app(monkeypatch)
    previous = setup_page(client)
    # A new session cannot be started before the prior owner explicitly stops.
    denied = post(client, "new", previous)
    assert denied.status_code == 409
    assert get(client, hosted.API + "status.json", previous).status_code == 200

    state["now"] = BASE + timedelta(seconds=30)
    accepted = post(client, "tick", previous, SAMPLE)
    assert accepted.status_code == 200 and accepted.json["accepted_ticks"] == 1
    stopped = post(client, "stop", previous)
    assert stopped.status_code == 200
    started = post(client, "new", previous)
    assert started.status_code == 200
    current = started.json["new_rehearsal_token"]
    assert started.json["previous_token_revoked"] is True
    assert current != previous and len(current) >= 32
    assert started.json["accepted_ticks"] == 0
    for path in ("status.json", "sample.json"):
        assert get(client, hosted.API + path, previous).status_code == 403
        fresh = get(client, hosted.API + path, current)
        assert fresh.status_code == 200
        assert "new_rehearsal_token" not in fresh.json
        assert "previous_token_revoked" not in fresh.json
    assert post(client, "pause", previous).status_code == 403
    assert post(client, "new", previous).status_code == 403
    assert post(client, "tick", previous, SAMPLE).status_code == 403
    assert get(client, hosted.API + "status.json", current).json["accepted_ticks"] == 0


def test_062_page_new_token_and_tower_session_rotation(monkeypatch):
    _, client, state = build_app(monkeypatch)
    old = setup_page(client)
    state["now"] += timedelta(seconds=30)
    assert post(client, "stop", old).status_code == 200
    rotated = post(client, "new", old).json["new_rehearsal_token"]
    # GET page of same scope returns only the current token; never revives old.
    from_page = setup_page(client)
    assert from_page == rotated and from_page != old
    assert get(client, hosted.API + "status.json", old).status_code == 403
    with client.session_transaction(base_url=ORIGIN) as cookie:
        cookie["tower-session"] = "new-tower-session-rotated-for-test"
    assert get(client, hosted.API + "status.json", rotated).status_code == 409
    later = setup_page(client)
    assert later != rotated
    assert get(client, hosted.API + "status.json", rotated).status_code == 403


def test_063_original_browser_acknowledges_rotation_before_refresh():
    browser = (ROOT / "web/static/ob/ob_hosted_owner_rehearsal.js").read_text()
    assert "let token = root.dataset.obCsrf;" in browser
    assert 'if (path === "/ob/owner-rehearsal/new.json")' in browser
    assert "result.previous_token_revoked !== true" in browser
    assert "result.new_rehearsal_token === token" in browser
    assert "token = result.new_rehearsal_token;" in browser
    assert "root.dataset.obCsrf = token;" in browser
    assert browser.index("token = result.new_rehearsal_token;") < browser.index("await refresh();")
    assert "localStorage" not in browser and "innerHTML" not in browser


def test_064_server_rechecks_workspace_and_token_under_same_mutation_lock():
    source = (ROOT / "tower/ob_hosted_owner_rehearsal.py").read_text()
    assert source.count("workspaces.get(key) is not item") == 2
    assert source.count('"REHEARSAL_SESSION_ROTATED_REENTER_TOWER"') == 2
    assert "new_item.csrf = item.csrf" not in source
    assert 'payload["new_rehearsal_token"] = new_item.csrf' in source
    assert 'payload["previous_token_revoked"] = True' in source
    assert "workspaces[key] = new_item" in source


def test_065_no_browser_reset_promotes_live_or_durable_authority(monkeypatch):
    _, client, state = build_app(monkeypatch)
    previous = setup_page(client)
    state["now"] += timedelta(seconds=30)
    assert post(client, "stop", previous).status_code == 200
    renewed = post(client, "new", previous).json
    assert renewed["durable_archive"] is False
    assert renewed["restart_recovery"] is False
    assert renewed["manual_live_unlock"] is False
    assert renewed["broker_submission"] is False
    assert renewed["capital_movement"] is False
    assert renewed["proof_demo_only"] is True
    assert renewed["source_provider_authenticated"] is False
    assert renewed["state"] == "RUNNING"
    assert renewed["accepted_ticks"] == 0
    # No token can create a real provider or broker action.
    current = renewed["new_rehearsal_token"]
    source = get(client, hosted.API + "status.json", current).json
    assert source["actual_capital_known"] is False
    assert source["automated_unlock"] is False
