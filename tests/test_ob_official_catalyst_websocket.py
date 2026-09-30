"""Synthetic-only WS invalidation tests; never contact public sources or a broker."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from flask import Flask

from engine.market_intake.official_catalyst_stream import (
    OfficialCatalystEventHub, SOURCES,
)
import web.ob_official_catalyst_websocket as websocket
from web.ob_official_catalyst_route import create_official_catalyst_blueprint

ROOT = Path(__file__).resolve().parents[1]


def held_packet():
    return {
        "schema": "OB_OFFICIAL_CATALYST_RADAR_V1",
        "sources": [{
            "source": source,
            "state": "EXISTING_PROTECTED_CORRIDOR" if source == "sec_edgar" else "REVIEW_HOLD",
            "facts": [],
            "ai_use_approved": False,
            "quote_eligible": False,
            "execution_authorized": False,
        } for source in SOURCES],
        "prices_attached": False,
        "broker_execution_authorized": False,
    }


def verified_packet():
    result = held_packet()
    row = result["sources"][0]
    row["state"] = "SOURCE_BOUND"
    row["ai_use_approved"] = True
    row["facts"] = [{
        "title": "Synthetic publication, never a live receipt",
        "period": "2025-08-19",
        "reference": "https://www.federalregister.gov/d/2025-12345",
        "id": "2025-12345", "stage": "Notice",
    }]
    return result


def test_invalidation_is_content_free_idempotent_and_revocation_visible():
    hub = OfficialCatalystEventHub()
    p = verified_packet()
    hint = hub.observe(p)
    assert hint["cursor"] == 1
    assert hint["available"] is False
    assert hint["provider_stream_attached"] is False
    assert hub.observe(p)["cursor"] == 1
    assert "Synthetic publication" not in json.dumps(hub._events)
    assert "2025-12345" not in json.dumps(hub._events)
    held = held_packet()
    assert hub.observe(held)["cursor"] == 2
    assert hub.observe(held)["cursor"] == 2
    assert hub._events[-1]["type"] == "snapshot_changed"
    assert hub._events[-1]["needs_authenticated_snapshot"] is True
    assert hub._events[-1]["execution_authorized"] is False
    assert hub._events[-1]["live_market_feed"] is False


def test_packet_rejects_fake_quote_or_unreviewed_held_payload():
    hub = OfficialCatalystEventHub()
    packet = verified_packet()
    packet["prices_attached"] = True
    with pytest.raises(ValueError, match="STREAM_PACKET_HOLD"):
        hub.observe(packet)
    packet["prices_attached"] = False
    packet["sources"][1]["facts"] = [{"secret": "unreviewed"}]
    with pytest.raises(ValueError, match="STREAM_PACKET_HOLD"):
        hub.observe(packet)
    assert hub.hint()["cursor"] == 0


def test_replay_restart_budget_and_queue_overflow_force_resync():
    async def run():
        hub = OfficialCatalystEventHub(history=8, queue_size=2, client_budget=1)
        hub.observe(verified_packet())
        key, queue, replay, hint = hub.subscribe(
            epoch=hub.epoch, cursor=0, loop=asyncio.get_running_loop())
        assert [x["type"] for x in replay] == ["snapshot_changed"]
        assert hint["cursor"] == 1
        with pytest.raises(ValueError, match="STREAM_CLIENT_BUDGET_HOLD"):
            hub.subscribe(epoch=hub.epoch, cursor=1,
                          loop=asyncio.get_running_loop())
        modified = verified_packet()
        modified["sources"][0]["facts"][0]["stage"] = "Rule"
        hub.observe(modified)
        hub.observe(held_packet())
        hub.observe(verified_packet())
        await asyncio.sleep(0)
        assert queue.full()
        pending = [queue.get_nowait() for _ in range(queue.qsize())]
        assert any(x["type"] == "resync_required" for x in pending)
        hub.unsubscribe(key)
        key2, _, old, _ = hub.subscribe(
            epoch="0" * 24, cursor=2, loop=asyncio.get_running_loop())
        assert old[0]["type"] == "resync_required"
        hub.unsubscribe(key2)
        assert OfficialCatalystEventHub().epoch != hub.epoch
    asyncio.run(run())


def scope(*, path=websocket.PATH, origin="https://tower.example",
          cookie="session=signed", query=None):
    if query is None:
        query = b"epoch=" + b"0" * 24 + b"&cursor=0"
    return {
        "type": "websocket", "path": path, "query_string": query,
        "headers": [
            (b"host", b"tower.example"), (b"origin", origin.encode()),
            (b"cookie", cookie.encode()),
        ],
    }


async def simulate(ws_scope, flask_app, receives):
    sent = []
    waiting = iter(receives)

    async def receive():
        return next(waiting)

    async def send(item):
        sent.append(item)

    await websocket.official_catalyst_websocket(
        ws_scope, receive, send, flask_app=flask_app,
    )
    return sent


def test_handshake_rejects_cross_origin_unsigned_owner_and_unknown_routes(monkeypatch):
    app = Flask(__name__)
    app.secret_key = "synthetic-only"
    app.extensions["ob_official_catalyst_event_hub"] = OfficialCatalystEventHub()
    monkeypatch.setenv("OB_CATALYST_WS_ASGI_ENABLED", "1")
    monkeypatch.setattr(websocket, "_authorize_owner",
                        lambda _app, cookie: cookie == "session=signed")
    for candidate in (
        scope(origin="https://evil.example"),
        scope(cookie="session=unsigned"),
        scope(path=websocket.PATH + "/alias"),
        scope(origin="http://tower.example"),
    ):
        sent = asyncio.run(simulate(candidate, app, []))
        assert sent == [{"type": "websocket.close", "code": websocket.CLOSE_DENIED}]
    assert not app.extensions["ob_official_catalyst_event_hub"]._clients


def test_exact_owner_receives_invalidation_only_and_no_client_commands(monkeypatch):
    app = Flask(__name__)
    app.secret_key = "synthetic-only"
    hub = OfficialCatalystEventHub()
    hub.observe(verified_packet())
    app.extensions["ob_official_catalyst_event_hub"] = hub
    monkeypatch.setenv("OB_CATALYST_WS_ASGI_ENABLED", "1")
    monkeypatch.setattr(websocket, "_authorize_owner",
                        lambda _app, cookie: cookie == "session=signed")
    ws_scope = scope(query=("epoch=" + hub.epoch + "&cursor=0").encode())
    sent = asyncio.run(simulate(ws_scope, app, [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1000},
    ]))
    assert sent[0]["type"] == "websocket.accept"
    packets = [json.loads(x["text"]) for x in sent if x["type"] == "websocket.send"]
    assert [x["type"] for x in packets] == ["stream_ready", "snapshot_changed"]
    assert all(x["source_only"] and not x["live_market_feed"] and
               not x["execution_authorized"] for x in packets)
    assert "Synthetic publication" not in json.dumps(packets)
    assert not hub._clients
    sent = asyncio.run(simulate(
        ws_scope, app, [{"type": "websocket.connect"},
                        {"type": "websocket.receive", "text": '{"place_order":true}'}]))
    assert sent[-1] == {"type": "websocket.close", "code": websocket.CLOSE_INPUT}
    assert not hub._clients


def test_default_off_and_cookie_signature_validation(monkeypatch):
    app = Flask(__name__)
    app.secret_key = "synthetic-only"
    app.extensions["ob_official_catalyst_event_hub"] = OfficialCatalystEventHub()
    monkeypatch.delenv("OB_CATALYST_WS_ASGI_ENABLED", raising=False)
    assert asyncio.run(simulate(scope(), app, []))[0]["code"] == websocket.CLOSE_DENIED
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["synthetic_owner"] = True
        cookie = client.get_cookie("session")
        assert cookie is not None
        raw = "session=" + cookie.value
    from flask import session
    def signed_check(cookie_header):
        with app.test_request_context("/ob/research/catalysts.json",
                                      headers={"Cookie": cookie_header}):
            return session.get("synthetic_owner") is True
    assert signed_check(raw)
    assert not signed_check("session=bad.signature")
    assert not signed_check("")


def test_authenticated_rest_attaches_safe_hint_and_does_not_raise_feed_claims(monkeypatch):
    class Service:
        def snapshot(self): return verified_packet()
    app = Flask(__name__)
    app.secret_key = "synthetic-only"
    hub = OfficialCatalystEventHub()
    app.register_blueprint(create_official_catalyst_blueprint(
        owner_authorize=lambda: True, catalyst_service=Service(), event_hub=hub))
    monkeypatch.delenv("OB_CATALYST_WS_ASGI_ENABLED", raising=False)
    first = app.test_client().get("/ob/research/catalysts.json")
    assert first.status_code == 200
    data = first.get_json()
    assert data["stream"]["available"] is False
    assert data["stream"]["cursor"] == 1
    assert data["stream"]["path"] == websocket.PATH
    assert "session" not in json.dumps(data["stream"]).lower()
    monkeypatch.setenv("OB_CATALYST_WS_ASGI_ENABLED", "1")
    later = app.test_client().get("/ob/research/catalysts.json").get_json()
    assert later["stream"]["available"] is True
    assert later["stream"]["cursor"] == 1


def test_staged_single_worker_and_ui_recovers_through_same_protected_get():
    start = (ROOT/"deploy/hosted_tower/start.sh").read_text()
    req = (ROOT/"deploy/hosted_tower/requirements.txt").read_text()
    script = (ROOT/"web/static/ob/ob_official_catalyst_radar.js").read_text()
    asgi = (ROOT/"web/hosted_tower_asgi.py").read_text()
    assert "OB_CATALYST_WS_ASGI_ENABLED" in start
    assert '--workers 1' in start and '--lifespan off' in start
    assert 'web.hosted_tower_asgi:application' in start
    assert 'web.hosted_tower:app' in start
    assert "asgiref" in req and "uvicorn" in req
    assert 'http_app = WsgiToAsgi(flask_app)' in asgi
    assert 'if scope.get("path") != PATH:' in asgi
    assert "new window.WebSocket(url)" in script
    assert "loadSnapshot(false)" in script
    assert '"/ob/research/catalysts.json"' in script
    assert 'credentials: "same-origin"' in script
    assert "innerHTML" not in script
    assert "api.eia.gov" not in script
    assert "api.public.com" not in script
