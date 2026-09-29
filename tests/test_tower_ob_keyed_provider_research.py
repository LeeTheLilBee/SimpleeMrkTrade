"""Offline tests for authenticated keyed-provider research dissemination.

No real provider traffic, credentials, quotes or broker calls.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

from flask import Flask
import pytest

from tower.ob_keyed_provider_research import (
    PATH, ProviderResearchCache, create_keyed_provider_research_blueprint,
    provider_research_projection,
)
from tower.ob_route_guard import match_ob_guard_policy
from tower.ob_web_route_enforcement import PROTECTED_EXACT_OB_ROUTES


class Response:
    def __init__(self, url, payload):
        self.status = 200
        self._url = url
        self._body = json.dumps(payload).encode()

    def geturl(self):
        return self._url

    def read(self, limit):
        return self._body[:limit]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class Recorder:
    def __init__(self):
        self.calls = []

    def open(self, request, timeout):
        self.calls.append((request, timeout))
        if "finnhub.io/api/v1/stock/profile2" in request.full_url:
            return Response(request.full_url, {
                "ticker": "AAPL", "name": "Apple Inc",
                "exchange": "NASDAQ NMS - GLOBAL MARKET",
                "finnhubIndustry": "Technology", "ipo": "1980-12-12",
                "marketCapitalization": 999999999,
            })
        if "alphavantage.co/query" in request.full_url:
            return Response(request.full_url, {
                "Meta Data": {"2. Symbol": "AAPL"},
                "Time Series (Daily)": {
                    "2026-09-28": {"1. open":"100","2. high":"104","3. low":"99","4. close":"103","5. volume":"1000"},
                    "2026-09-25": {"1. open":"98","2. high":"101","3. low":"97","4. close":"100","5. volume":"900"},
                    "2026-09-24": {"1. open":"97","2. high":"99","3. low":"96","4. close":"98","5. volume":"800"},
                }
            })
        raise AssertionError("unexpected URL")


def secret_reader(sid, provider):
    assert sid.startswith("tower_session_")
    return SimpleNamespace(value="SECRET-" + provider)


@pytest.fixture
def rights(monkeypatch):
    monkeypatch.setenv("OB_PROVIDER_RESEARCH_FETCH_ENABLED", "1")
    for provider in ("FINNHUB", "ALPHA_VANTAGE"):
        monkeypatch.setenv(f"OB_PROVIDER_{provider}_SOURCE_USE_REVIEWED", "1")
        monkeypatch.setenv(f"OB_PROVIDER_{provider}_OWNER_DISPLAY_REVIEWED", "1")
        monkeypatch.delenv(f"OB_PROVIDER_{provider}_AI_USE_REVIEWED", raising=False)


def test_exact_route_is_owner_mapped_and_get_only():
    assert PATH in PROTECTED_EXACT_OB_ROUTES
    decision = match_ob_guard_policy(PATH)
    assert decision["match_type"] == "exact"
    assert decision["policy"]["route_key"] == "data_desk"
    assert match_ob_guard_policy(PATH + "/extra")["match_type"] == "unmapped_default_deny"


def test_no_key_never_calls_provider(monkeypatch):
    monkeypatch.setenv("OB_PROVIDER_RESEARCH_FETCH_ENABLED", "1")
    rec = Recorder()
    packet = provider_research_projection(
        sid="tower_session_" + "x"*20, symbol="AAPL",
        secret_reader=lambda *_: None, opener=rec, cache=ProviderResearchCache())
    assert not rec.calls
    assert [x["state"] for x in packet["provider_research"]] == ["NOT_CONNECTED", "NOT_CONNECTED"]
    assert packet["soulaana_research"]["observations"] == []


def test_rights_hold_never_calls_provider(monkeypatch):
    monkeypatch.delenv("OB_PROVIDER_RESEARCH_FETCH_ENABLED", raising=False)
    rec = Recorder()
    packet = provider_research_projection(
        sid="tower_session_" + "x"*20, symbol="AAPL",
        secret_reader=secret_reader, opener=rec, cache=ProviderResearchCache())
    assert not rec.calls
    assert [x["state"] for x in packet["provider_research"]] == ["RIGHTS_OR_FETCH_HOLD"]*2


def test_source_bound_owner_projection_is_bounded_and_not_live(rights):
    rec = Recorder()
    packet = provider_research_projection(
        sid="tower_session_" + "x"*20, symbol="AAPL",
        secret_reader=secret_reader, opener=rec, cache=ProviderResearchCache())
    assert len(rec.calls) == 2
    assert packet["schema"] == "OB_KEYED_PROVIDER_RESEARCH_V1"
    assert packet["live_prices_attached"] is False
    assert packet["orders_attached"] is False
    assert packet["may_authorize_order"] is False
    finnhub, alpha = packet["provider_research"]
    assert finnhub["state"] == "SOURCE_BOUND"
    assert finnhub["security_name"] == "Apple Inc"
    assert "marketCapitalization" not in finnhub
    assert alpha["state"] == "SOURCE_BOUND"
    assert alpha["historical_only"] is True
    assert len(alpha["bars"]) == 3
    assert alpha["bars"][0]["session_date"] == "2026-09-28"
    assert "SECRET" not in json.dumps(packet)
    assert packet["soulaana_research"]["observations"] == []


def test_ai_content_requires_independent_per_provider_grant(rights, monkeypatch):
    monkeypatch.setenv("OB_PROVIDER_FINNHUB_AI_USE_REVIEWED", "1")
    rec = Recorder()
    packet = provider_research_projection(
        sid="tower_session_" + "x"*20, symbol="AAPL",
        secret_reader=secret_reader, opener=rec, cache=ProviderResearchCache())
    brief = packet["soulaana_research"]
    assert [x["provider"] for x in brief["observations"]] == ["finnhub"]
    item = brief["observations"][0]
    assert item["live_quote"] is False
    assert "bars" not in item
    assert brief["broker_execution_authorized"] is False
    assert brief["capital_authorized"] is False


def test_cache_avoids_repeat_provider_call_within_ttl(rights):
    rec = Recorder()
    cache = ProviderResearchCache()
    args = dict(sid="tower_session_"+"x"*20, symbol="AAPL",
                secret_reader=secret_reader, opener=rec, cache=cache)
    first = provider_research_projection(**args)
    second = provider_research_projection(**args)
    assert len(rec.calls) == 2
    assert first["provider_research"] == second["provider_research"]


def test_invalid_symbol_and_session_fail_before_network(rights):
    rec = Recorder()
    for sid, symbol in (("bad", "AAPL"), ("tower_session_"+"x"*20, "../AAPL"),
                        ("tower_session_"+"x"*20, "AAPL?x=1")):
        with pytest.raises(ValueError):
            provider_research_projection(
                sid=sid, symbol=symbol, secret_reader=secret_reader,
                opener=rec, cache=ProviderResearchCache())
    assert not rec.calls


def test_http_blueprint_requires_owner_and_current_sid(rights):
    rec = Recorder()
    state = {"owner": False}
    app = Flask(__name__)
    app.secret_key = "test-only"
    app.config["TESTING"] = True
    app.register_blueprint(create_keyed_provider_research_blueprint(
        owner_authorize=lambda: state["owner"], secret_reader=secret_reader, opener=rec))
    client = app.test_client()
    assert client.get(PATH+"?symbol=AAPL").status_code == 403
    state["owner"] = True
    assert client.get(PATH+"?symbol=AAPL").status_code == 403
    with client.session_transaction() as sess:
        sess["tower_session_id"] = "tower_session_"+"x"*20
    response = client.get(PATH+"?symbol=AAPL")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["symbol"] == "AAPL"
    assert response.headers["Cache-Control"].startswith("private, no-store")
    assert client.post(PATH+"?symbol=AAPL").status_code == 405
