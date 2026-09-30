"""Synthetic ObservatoryEventHub tests. No public source or broker calls."""
from __future__ import annotations

import asyncio
from copy import deepcopy
import json
from pathlib import Path

import pytest
from flask import Flask

from engine.market_intake.observatory_event_stream import ObservatoryEventHub
from engine.market_intake.official_catalyst_fingerprint import (
    SOURCES,
    official_catalyst_fingerprint,
)
import web.ob_event_websocket as websocket
from web.ob_official_catalyst_route import create_official_catalyst_blueprint

ROOT = Path(__file__).resolve().parents[1]


def held_packet():
    return {
        "schema": "OB_OFFICIAL_CATALYST_RADAR_V1",
        "sources": [{
            "source": source,
            "state": (
                "EXISTING_PROTECTED_CORRIDOR"
                if source == "sec_edgar" else "REVIEW_HOLD"
            ),
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
    result["sources"][0].update({
        "state": "SOURCE_BOUND",
        "ai_use_approved": True,
        "facts": [{
            "title": "Synthetic publication, never a live receipt",
            "period": "2026-09-29",
            "reference": "https://www.federalregister.gov/d/2026-12345",
            "id": "2026-12345",
            "stage": "Notice",
        }],
    })
    return result


def observe_catalyst(hub, packet):
    return hub.observe_digest(
        observation_key="official_catalyst_radar:snapshot",
        digest=official_catalyst_fingerprint(packet),
        event_type="research_context_changed",
        source="official_catalyst_radar",
        snapshot_path="/ob/research/catalysts.json",
    )


def test_catalyst_fingerprint_rejects_fake_quote_and_unreviewed_payload():
    packet = verified_packet()
    digest = official_catalyst_fingerprint(packet)
    assert len(digest) == 64
    assert digest == official_catalyst_fingerprint(deepcopy(packet))

    changed = deepcopy(packet)
    changed["sources"][0]["facts"][0]["stage"] = "Rule"
    assert official_catalyst_fingerprint(changed) != digest

    fake = deepcopy(packet)
    fake["prices_attached"] = True
    with pytest.raises(ValueError, match="CATALYST_FINGERPRINT_PACKET_HOLD"):
        official_catalyst_fingerprint(fake)

    held = deepcopy(packet)
    held["sources"][1]["facts"] = [{"secret": "unreviewed"}]
    with pytest.raises(ValueError, match="CATALYST_FINGERPRINT_PACKET_HOLD"):
        official_catalyst_fingerprint(held)


def test_one_hub_is_content_free_idempotent_and_multichannel():
    hub = ObservatoryEventHub()
    assert observe_catalyst(hub, verified_packet())["cursor"] == 1
    assert observe_catalyst(hub, verified_packet())["cursor"] == 1

    event = hub._events[-1]
    assert event["type"] == "research_context_changed"
    assert event["channel"] == "research"
    assert event["snapshot_path"] == "/ob/research/catalysts.json"
    assert event["content_attached"] is False
    assert event["provider_payload_attached"] is False
    assert event["live_quote_payload_attached"] is False
    assert event["current_quote_verified"] is False
    assert event["execution_authorized"] is False
    encoded = json.dumps(list(hub._events))
    assert "Synthetic publication" not in encoded
    assert "2026-12345" not in encoded

    hub.publish_invalidation(
        event_type="source_status_changed",
        source="provider_status",
        snapshot_path="/ob/data-desk/connections.json",
    )
    assert hub._events[-1]["channel"] == "system"

    with pytest.raises(ValueError, match="SNAPSHOT_PATH_HOLD"):
        hub.publish_invalidation(
            event_type="market_snapshot_changed",
            source="provider",
            snapshot_path="https://evil.example/raw",
        )
    with pytest.raises(ValueError, match="SOURCE_HOLD"):
        hub.publish_invalidation(
            event_type="source_status_changed",
            source="../provider",
            snapshot_path="/ob/data-desk/connections.json",
        )


def test_replay_restart_budget_overflow_and_session_revocation():
    async def run():
        hub = ObservatoryEventHub(history=8, queue_size=2, client_budget=1)
        observe_catalyst(hub, verified_packet())
        key, queue, replay, hint = hub.subscribe(
            epoch=hub.epoch,
            cursor=0,
            loop=asyncio.get_running_loop(),
        )
        assert [x["type"] for x in replay] == ["research_context_changed"]
        assert hint["cursor"] == 1

        with pytest.raises(ValueError, match="CLIENT_BUDGET_HOLD"):
            hub.subscribe(
                epoch=hub.epoch,
                cursor=1,
                loop=asyncio.get_running_loop(),
            )

        for source in ("one", "two", "three"):
            hub.publish_invalidation(
                event_type="source_status_changed",
                source=source,
                snapshot_path="/ob/data-desk/connections.json",
            )
        await asyncio.sleep(0)
        queued = [queue.get_nowait() for _ in range(queue.qsize())]
        assert any(x["type"] == "resync_required" for x in queued)
        hub.unsubscribe(key)

        key2, _, replay2, _ = hub.subscribe(
            epoch="0" * 24,
            cursor=0,
            loop=asyncio.get_running_loop(),
        )
        assert replay2[0]["type"] == "resync_required"
        hub.unsubscribe(key2)
        assert ObservatoryEventHub().epoch != hub.epoch

        hub.revoke_session("tower_session_synthetic")
        assert hub.session_revoked("tower_session_synthetic") is True
        assert hub.session_revoked("tower_session_other") is False

    asyncio.run(run())


def scope(*, path=websocket.PATH, origin="https://tower.example",
          cookie="session=signed", query=None):
    if query is None:
        query = b"epoch=" + b"0" * 24 + b"&cursor=0"
    return {
        "type": "websocket",
        "path": path,
        "query_string": query,
        "headers": [
            (b"host", b"tower.example"),
            (b"origin", origin.encode()),
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

    await websocket.observatory_event_websocket(
        ws_scope,
        receive,
        send,
        flask_app=flask_app,
    )
    return sent


def test_handshake_rejects_cross_origin_unsigned_and_unknown_routes(monkeypatch):
    app = Flask(__name__)
    app.secret_key = "synthetic-only"
    app.extensions["ob_observatory_event_hub"] = ObservatoryEventHub()
    monkeypatch.setenv("OB_EVENT_WS_ASGI_ENABLED", "1")
    monkeypatch.setattr(
        websocket,
        "_authorize_owner",
        lambda _app, cookie: cookie == "session=signed",
    )
    for candidate in (
        scope(origin="https://evil.example"),
        scope(cookie="session=unsigned"),
        scope(path=websocket.PATH + "/alias"),
        scope(origin="http://tower.example"),
    ):
        sent = asyncio.run(simulate(candidate, app, []))
        assert sent == [{
            "type": "websocket.close",
            "code": websocket.CLOSE_DENIED,
        }]
    assert not app.extensions["ob_observatory_event_hub"]._clients


def test_owner_receives_shared_events_and_client_commands_are_rejected(monkeypatch):
    app = Flask(__name__)
    app.secret_key = "synthetic-only"
    hub = ObservatoryEventHub()
    observe_catalyst(hub, verified_packet())
    hub.publish_invalidation(
        event_type="scanner_context_changed",
        source="scanner",
        snapshot_path="/ob/engine-feed-snapshot.json",
        symbol="AAPL",
    )
    app.extensions["ob_observatory_event_hub"] = hub

    monkeypatch.setenv("OB_EVENT_WS_ASGI_ENABLED", "1")
    monkeypatch.setattr(
        websocket,
        "_authorize_owner",
        lambda _app, cookie: cookie == "session=signed",
    )
    ws_scope = scope(
        query=("epoch=" + hub.epoch + "&cursor=0").encode()
    )
    sent = asyncio.run(simulate(ws_scope, app, [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1000},
    ]))
    assert sent[0]["type"] == "websocket.accept"
    packets = [
        json.loads(x["text"])
        for x in sent
        if x["type"] == "websocket.send"
    ]
    assert [x["type"] for x in packets] == [
        "stream_ready",
        "research_context_changed",
        "scanner_context_changed",
    ]
    assert all(x["content_attached"] is False for x in packets)
    assert all(x["provider_payload_attached"] is False for x in packets)
    assert all(x["execution_authorized"] is False for x in packets)
    assert "Synthetic publication" not in json.dumps(packets)
    assert not hub._clients

    sent = asyncio.run(simulate(ws_scope, app, [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": '{"place_order":true}'},
    ]))
    assert sent[-1] == {
        "type": "websocket.close",
        "code": websocket.CLOSE_INPUT,
    }


def test_default_off():
    app = Flask(__name__)
    app.secret_key = "synthetic-only"
    app.extensions["ob_observatory_event_hub"] = ObservatoryEventHub()
    sent = asyncio.run(simulate(scope(), app, []))
    assert sent == [{
        "type": "websocket.close",
        "code": websocket.CLOSE_DENIED,
    }]


def test_catalyst_rest_uses_same_hub_and_emits_only_on_real_change(monkeypatch):
    class Service:
        def __init__(self):
            self.packet = verified_packet()

        def snapshot(self):
            return deepcopy(self.packet)

    app = Flask(__name__)
    app.secret_key = "synthetic-only"
    hub = ObservatoryEventHub()
    service = Service()
    app.register_blueprint(create_official_catalyst_blueprint(
        owner_authorize=lambda: True,
        catalyst_service=service,
        observatory_event_hub=hub,
    ))
    monkeypatch.setenv("OB_EVENT_WS_ASGI_ENABLED", "1")

    client = app.test_client()
    first = client.get("/ob/research/catalysts.json")
    assert first.status_code == 200
    data = first.get_json()
    assert data["event_stream"]["available"] is True
    assert data["event_stream"]["cursor"] == 1
    assert data["event_stream"]["path"] == websocket.PATH

    second = client.get("/ob/research/catalysts.json")
    assert second.status_code == 200
    assert second.get_json()["event_stream"]["cursor"] == 1

    service.packet["sources"][0]["facts"][0]["stage"] = "Rule"
    third = client.get("/ob/research/catalysts.json")
    assert third.status_code == 200
    assert third.get_json()["event_stream"]["cursor"] == 2


def test_staged_single_socket_and_ui_recovers_through_protected_get():
    start = (ROOT / "deploy/hosted_tower/start.sh").read_text()
    req = (ROOT / "deploy/hosted_tower/requirements.txt").read_text()
    script = (ROOT / "web/static/ob/ob_official_catalyst_radar.js").read_text()
    asgi = (ROOT / "web/hosted_tower_asgi.py").read_text()

    assert "OB_EVENT_WS_ASGI_ENABLED" in start
    assert "OB_CATALYST_WS_ASGI_ENABLED" not in start
    assert "OB_MARKET_WS_ASGI_ENABLED" not in start
    assert "--workers 1" in start and "--lifespan off" in start
    assert "web.hosted_tower_asgi:application" in start
    assert "web.hosted_tower:app" in start
    assert "asgiref" in req and "uvicorn" in req

    assert "http_app = WsgiToAsgi(flask_app)" in asgi
    assert 'if scope.get("path") != PATH:' in asgi
    assert "observatory_event_websocket" in asgi

    assert "OB_EVENT_STREAM_HINT_V1" in script
    assert '"/ob/events/stream"' in script
    assert "new window.WebSocket(url)" in script
    assert "research_context_changed" in script
    assert "loadSnapshot(false)" in script
    assert '"/ob/research/catalysts.json"' in script
    assert 'credentials: "same-origin"' in script
    assert "innerHTML" not in script
    assert "api.eia.gov" not in script
    assert "api.public.com" not in script


def test_old_signed_cookie_loses_event_socket_and_research_get_after_logout(monkeypatch):
    from flask import session
    from tower.tower_human_login_ob_launch import (
        SESSION_ID,
        _revoke_previous_observatory_event_session,
    )
    import tower.ob_market_data_desk_integration as desk

    class Service:
        def snapshot(self):
            return verified_packet()

    app = Flask(__name__)
    app.secret_key = "synthetic-only"
    hub = ObservatoryEventHub()
    app.extensions["ob_observatory_event_hub"] = hub
    app.register_blueprint(create_official_catalyst_blueprint(
        owner_authorize=lambda: session.get("synthetic_owner") is True,
        catalyst_service=Service(),
        observatory_event_hub=hub,
    ))

    with app.test_client() as client:
        with client.session_transaction() as owner:
            owner["synthetic_owner"] = True
            owner[SESSION_ID] = "tower_session_synthetic_random_id"
        signed_cookie = client.get_cookie("session")
        assert signed_cookie
        raw = "session=" + signed_cookie.value
        assert client.get("/ob/research/catalysts.json").status_code == 200

    monkeypatch.setattr(
        desk,
        "_tower_authorize_data_desk",
        lambda: session.get("synthetic_owner") is True,
    )
    assert websocket._authorize_owner(app, raw) is True

    with app.test_request_context("/tower/logout", headers={"Cookie": raw}):
        _revoke_previous_observatory_event_session()
        session.clear()

    assert hub.session_revoked("tower_session_synthetic_random_id") is True
    assert websocket._authorize_owner(app, raw) is False

    with app.test_client() as client:
        client.set_cookie("session", signed_cookie.value)
        assert client.get("/ob/research/catalysts.json").status_code == 403
