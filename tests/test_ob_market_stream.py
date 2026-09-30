"""Synthetic MarketStreamHub/WebSocket tests. No provider or broker calls."""
from __future__ import annotations

import asyncio
from copy import deepcopy
import json
from pathlib import Path

import pytest
from flask import Flask

from engine.market_intake.market_stream import MarketStreamHub
from engine.market_intake.official_catalyst_stream import (
    OfficialCatalystEventHub,
    SOURCES,
)
import web.ob_market_websocket as market_ws
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
    packet = held_packet()
    packet["sources"][0].update({
        "state": "SOURCE_BOUND",
        "ai_use_approved": True,
        "facts": [{
            "title": "Synthetic source fact",
            "period": "2026-09-29",
            "reference": "https://www.federalregister.gov/d/2026-12345",
            "id": "2026-12345",
            "stage": "Notice",
        }],
    })
    return packet


def test_market_hub_is_content_free_and_paths_are_fixed():
    hub = MarketStreamHub()
    event = hub.publish_invalidation(
        event_type="research_context_changed",
        source="official_catalyst_radar",
        snapshot_path="/ob/research/catalysts.json",
    )
    assert event["cursor"] == 1
    assert event["channel"] == "research"
    assert event["content_attached"] is False
    assert event["provider_payload_attached"] is False
    assert event["provider_stream_attached"] is False
    assert event["live_quote_payload_attached"] is False
    assert event["current_quote_verified"] is False
    assert event["execution_authorized"] is False
    encoded = json.dumps(event).lower()
    assert "bid" not in encoded and "ask" not in encoded and "last_price" not in encoded
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


def test_market_hub_replay_restart_capacity_and_overflow_resync():
    async def run():
        hub = MarketStreamHub(history=8, queue_size=2, client_budget=1)
        hub.publish_invalidation(
            event_type="research_context_changed",
            source="official_catalyst_radar",
            snapshot_path="/ob/research/catalysts.json",
        )
        key, queue, replay, hint = hub.subscribe(
            epoch=hub.epoch, cursor=0, loop=asyncio.get_running_loop()
        )
        assert [x["type"] for x in replay] == ["research_context_changed"]
        assert hint["cursor"] == 1
        with pytest.raises(ValueError, match="CLIENT_BUDGET_HOLD"):
            hub.subscribe(
                epoch=hub.epoch, cursor=1, loop=asyncio.get_running_loop()
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
            epoch="0" * 24, cursor=0, loop=asyncio.get_running_loop()
        )
        assert replay2[0]["type"] == "resync_required"
        hub.unsubscribe(key2)
        assert MarketStreamHub().epoch != hub.epoch

    asyncio.run(run())


def scope(*, origin="https://tower.example", cookie="session=signed", query=None):
    if query is None:
        query = b"epoch=" + b"0" * 24 + b"&cursor=0"
    return {
        "type": "websocket",
        "path": market_ws.PATH,
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

    await market_ws.market_stream_websocket(
        ws_scope, receive, send, flask_app=flask_app
    )
    return sent


def app_with_hubs():
    app = Flask(__name__)
    app.secret_key = "synthetic-only"
    app.extensions["ob_official_catalyst_event_hub"] = OfficialCatalystEventHub()
    app.extensions["ob_market_stream_event_hub"] = MarketStreamHub()
    return app


def test_market_websocket_auth_origin_replay_and_no_command_protocol(monkeypatch):
    app = app_with_hubs()
    hub = app.extensions["ob_market_stream_event_hub"]
    hub.publish_invalidation(
        event_type="research_context_changed",
        source="official_catalyst_radar",
        snapshot_path="/ob/research/catalysts.json",
    )
    monkeypatch.setenv("OB_MARKET_WS_ASGI_ENABLED", "1")
    monkeypatch.setattr(
        market_ws, "_authorize_owner",
        lambda _app, cookie: cookie == "session=signed",
    )
    good = scope(
        query=("epoch=" + hub.epoch + "&cursor=0").encode()
    )
    sent = asyncio.run(simulate(good, app, [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1000},
    ]))
    assert sent[0]["type"] == "websocket.accept"
    packets = [
        json.loads(item["text"])
        for item in sent
        if item["type"] == "websocket.send"
    ]
    assert [item["type"] for item in packets] == [
        "stream_ready", "research_context_changed"
    ]
    assert all(item["provider_payload_attached"] is False for item in packets)

    denied = asyncio.run(simulate(
        scope(origin="https://evil.example"), app, []
    ))
    assert denied == [{"type": "websocket.close", "code": 4403}]

    sent = asyncio.run(simulate(good, app, [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": '{"subscribe":"AAPL"}'},
    ]))
    assert sent[-1] == {"type": "websocket.close", "code": 4400}


def test_market_websocket_default_off(monkeypatch):
    app = app_with_hubs()
    monkeypatch.delenv("OB_MARKET_WS_ASGI_ENABLED", raising=False)
    monkeypatch.setattr(market_ws, "_authorize_owner", lambda *_: True)
    sent = asyncio.run(simulate(scope(), app, []))
    assert sent == [{"type": "websocket.close", "code": 4403}]


def test_catalyst_bridge_emits_once_per_actual_snapshot_change(monkeypatch):
    class Service:
        def __init__(self):
            self.packet = verified_packet()

        def snapshot(self):
            return deepcopy(self.packet)

    app = Flask(__name__)
    app.secret_key = "synthetic-only"
    catalyst_hub = OfficialCatalystEventHub()
    market_hub = MarketStreamHub()
    service = Service()
    app.register_blueprint(create_official_catalyst_blueprint(
        owner_authorize=lambda: True,
        catalyst_service=service,
        event_hub=catalyst_hub,
        market_event_hub=market_hub,
    ))
    monkeypatch.setenv("OB_MARKET_WS_ASGI_ENABLED", "1")

    client = app.test_client()
    first = client.get("/ob/research/catalysts.json")
    assert first.status_code == 200
    body = first.get_json()
    assert body["market_stream"]["available"] is True
    assert body["market_stream"]["cursor"] == 1

    second = client.get("/ob/research/catalysts.json")
    assert second.status_code == 200
    assert second.get_json()["market_stream"]["cursor"] == 1

    service.packet["sources"][0]["facts"][0]["stage"] = "Rule"
    third = client.get("/ob/research/catalysts.json")
    assert third.status_code == 200
    assert third.get_json()["market_stream"]["cursor"] == 2
    event = market_hub._events[-1]
    assert event["type"] == "research_context_changed"
    assert event["snapshot_path"] == "/ob/research/catalysts.json"
    assert event["content_attached"] is False


def test_asgi_and_startup_support_both_exact_ob_websockets():
    asgi = (ROOT / "web/hosted_tower_asgi.py").read_text()
    start = (ROOT / "deploy/hosted_tower/start.sh").read_text()
    assert "CATALYST_PATH" in asgi and "MARKET_PATH" in asgi
    assert "market_stream_websocket" in asgi
    assert "OB_CATALYST_WS_ASGI_ENABLED" in start
    assert "OB_MARKET_WS_ASGI_ENABLED" in start
    assert "--workers 1" in start
