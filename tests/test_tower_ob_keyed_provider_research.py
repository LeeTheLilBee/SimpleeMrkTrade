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
        if "finazon.io" in request.full_url:
            return Response(request.full_url, {
                "lt": {"p": 231.12, "s": 100, "tm": 1790760600000},
                "1d": {"o": 229.0, "h": 233.5, "l": 228.4, "c": 231.0, "v": 34567890},
                "p1d": {"c": 228.7},
                "52w": {"h": 260.1, "l": 170.2},
                "ch": {"dap": 1.0066},
            })
        if "apps.bea.gov/api/data" in request.full_url:
            return Response(request.full_url, {
                "BEAAPI": {"Results": {"Data": [
                    {"LineNumber": "1", "TimePeriod": "2026Q2", "DataValue": "31,250.0"},
                    {"LineNumber": "1", "TimePeriod": "2026Q1", "DataValue": "30,900.0"},
                    {"LineNumber": "2", "TimePeriod": "2026Q2", "DataValue": "2.7"},
                ]}}
            })
        raise AssertionError("unexpected URL")


def secret_reader(sid, provider):
    assert sid.startswith("tower_session_")
    return SimpleNamespace(value="SECRET-" + provider)


@pytest.fixture
def rights(monkeypatch):
    monkeypatch.setenv("OB_PROVIDER_RESEARCH_FETCH_ENABLED", "1")
    for provider in ("FINNHUB", "ALPHA_VANTAGE", "FINAZON", "BEA"):
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
    assert [x["state"] for x in packet["provider_research"]] == ["NOT_CONNECTED"] * 4
    assert packet["soulaana_research"]["observations"] == []


def test_rights_hold_never_calls_provider(monkeypatch):
    monkeypatch.delenv("OB_PROVIDER_RESEARCH_FETCH_ENABLED", raising=False)
    rec = Recorder()
    packet = provider_research_projection(
        sid="tower_session_" + "x"*20, symbol="AAPL",
        secret_reader=secret_reader, opener=rec, cache=ProviderResearchCache())
    assert not rec.calls
    assert [x["state"] for x in packet["provider_research"]] == ["RIGHTS_OR_FETCH_HOLD"]*4


def test_source_bound_owner_projection_is_bounded_and_not_live(rights):
    rec = Recorder()
    packet = provider_research_projection(
        sid="tower_session_" + "x"*20, symbol="AAPL",
        secret_reader=secret_reader, opener=rec, cache=ProviderResearchCache())
    assert len(rec.calls) == 4
    assert packet["schema"] == "OB_KEYED_PROVIDER_RESEARCH_V1"
    assert packet["live_prices_attached"] is True
    assert packet["orders_attached"] is False
    assert packet["may_authorize_order"] is False
    finnhub, alpha, finazon, bea = packet["provider_research"]
    assert finnhub["state"] == "SOURCE_BOUND"
    assert finnhub["security_name"] == "Apple Inc"
    assert "marketCapitalization" not in finnhub
    assert alpha["state"] == "SOURCE_BOUND"
    assert alpha["historical_only"] is True
    assert len(alpha["bars"]) == 3
    assert alpha["bars"][0]["session_date"] == "2026-09-28"
    assert finazon["state"] == "SOURCE_BOUND"
    assert finazon["real_time_market_context"] is True
    assert finazon["consolidated_quote"] is False
    assert bea["state"] == "SOURCE_BOUND"
    assert bea["kind"] == "OFFICIAL_US_QUARTERLY_GDP_CONTEXT"
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



def test_reviewed_provider_records_are_actually_examined_and_cited(rights, monkeypatch):
    monkeypatch.setenv("OB_PROVIDER_FINNHUB_AI_USE_REVIEWED", "1")
    monkeypatch.setenv("OB_PROVIDER_ALPHA_VANTAGE_AI_USE_REVIEWED", "1")
    packet = provider_research_projection(
        sid="tower_session_" + "x"*20, symbol="AAPL",
        secret_reader=secret_reader, opener=Recorder(), cache=ProviderResearchCache())
    brief = packet["soulaana_research"]
    assert brief["external_model_called"] is False
    assert [o["provider"] for o in brief["observations"]] == ["finnhub", "alpha_vantage"]
    profile, history = brief["observations"]
    assert "Apple Inc" in profile["finding"]
    assert "Technology" in profile["finding"]
    assert profile["source_reference"] == "https://finnhub.io/docs/api/company-profile2"
    assert "2026-09-28" in history["finding"]
    assert "2026-09-25" in history["finding"]
    assert "+3.00" in history["finding"]
    assert "+3.000%" in history["finding"]
    assert history["summary"]["close_change"] == "3.0"
    assert history["summary"]["close_change_percent"] == "+3.000"
    assert history["source_reference"] == "https://www.alphavantage.co/documentation/#daily"
    assert "SECRET" not in json.dumps(brief)
    assert "bars" not in json.dumps(brief)
    assert brief["live_quote_verified"] is False
    assert brief["candidate_admitted"] is False


def test_revoking_ai_grant_suppresses_findings_even_when_provider_is_cached(rights, monkeypatch):
    monkeypatch.setenv("OB_PROVIDER_FINNHUB_AI_USE_REVIEWED", "1")
    monkeypatch.setenv("OB_PROVIDER_ALPHA_VANTAGE_AI_USE_REVIEWED", "1")
    recorder, cache = Recorder(), ProviderResearchCache()
    args = dict(sid="tower_session_" + "x"*20, symbol="AAPL",
                secret_reader=secret_reader, opener=recorder, cache=cache)
    assert len(provider_research_projection(**args)["soulaana_research"]["observations"]) == 2
    monkeypatch.delenv("OB_PROVIDER_ALPHA_VANTAGE_AI_USE_REVIEWED")
    second = provider_research_projection(**args)
    assert len(recorder.calls) == 4  # no fresh provider call needed
    assert [o["provider"] for o in second["soulaana_research"]["observations"]] == ["finnhub"]
    monkeypatch.delenv("OB_PROVIDER_FINNHUB_AI_USE_REVIEWED")
    third = provider_research_projection(**args)["soulaana_research"]
    assert third["observations"] == []
    assert third["source_specific_ai_use_approved"] is False


def test_shared_panel_renders_reviewed_examination_not_only_connected_status():
    from pathlib import Path
    js = Path("web/static/ob/ob_keyless_context.js").read_text()
    assert "Soulaana · What I actually found" in js
    assert 'item.finding' in js and 'item.what_is_missing' in js
    assert "brief.external_model_called === false" in js
    assert "item.source_reference === refs[item.provider]" in js
    assert "record.append" in js and "textContent" in js
    assert "Soulaana can read only the provider research" not in js

def test_cache_avoids_repeat_provider_call_within_ttl(rights):
    rec = Recorder()
    cache = ProviderResearchCache()
    args = dict(sid="tower_session_"+"x"*20, symbol="AAPL",
                secret_reader=secret_reader, opener=rec, cache=cache)
    first = provider_research_projection(**args)
    second = provider_research_projection(**args)
    assert len(rec.calls) == 4
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


def test_finazon_free_trial_holds_symbols_outside_trial(rights):
    rec = Recorder()
    packet = provider_research_projection(
        sid="tower_session_" + "x"*20, symbol="MSFT",
        secret_reader=secret_reader, opener=rec, cache=ProviderResearchCache())
    finazon = packet["provider_research"][2]
    assert finazon["provider"] == "finazon"
    assert finazon["state"] == "FREE_TRIAL_SYMBOL_HOLD"
    assert finazon["eligible_trial_symbols"] == ["AAPL", "GOOG", "TSLA"]
    assert not any("finazon.io" in req.full_url for req, _ in rec.calls)


def test_finazon_and_bea_require_independent_ai_grants(rights, monkeypatch):
    monkeypatch.setenv("OB_PROVIDER_FINAZON_AI_USE_REVIEWED", "1")
    monkeypatch.setenv("OB_PROVIDER_BEA_AI_USE_REVIEWED", "1")
    packet = provider_research_projection(
        sid="tower_session_" + "x"*20, symbol="AAPL",
        secret_reader=secret_reader, opener=Recorder(), cache=ProviderResearchCache())
    observations = packet["soulaana_research"]["observations"]
    assert [x["provider"] for x in observations] == ["finazon", "bea"]
    assert "not SIP/NBBO" in observations[0]["finding"]
    assert "macroeconomic context" in observations[1]["finding"]
    assert packet["soulaana_research"]["live_quote_verified"] is False


def test_finazon_free_trial_noneligible_symbol_never_calls_finazon(rights):
    rec = Recorder()
    packet = provider_research_projection(
        sid="tower_session_" + "x"*20, symbol="MSFT",
        secret_reader=secret_reader, opener=rec, cache=ProviderResearchCache())
    finazon = next(row for row in packet["provider_research"] if row["provider"] == "finazon")
    assert finazon["state"] == "FREE_TRIAL_SYMBOL_HOLD"
    assert finazon["trial_access_state"] == "SYMBOL_NOT_IN_FREE_TRIAL"
    assert finazon["eligible_trial_symbols"] == ["AAPL", "GOOG", "TSLA"]
    assert not any("finazon.io" in call[0].full_url for call in rec.calls)


def test_finazon_and_bea_soulaana_require_independent_ai_grants(rights, monkeypatch):
    monkeypatch.setenv("OB_PROVIDER_FINAZON_AI_USE_REVIEWED", "1")
    monkeypatch.setenv("OB_PROVIDER_BEA_AI_USE_REVIEWED", "1")
    packet = provider_research_projection(
        sid="tower_session_" + "x"*20, symbol="AAPL",
        secret_reader=secret_reader, opener=Recorder(), cache=ProviderResearchCache())
    observations = packet["soulaana_research"]["observations"]
    assert [row["provider"] for row in observations] == ["finazon", "bea"]
    finazon, bea = observations
    assert "not SIP/NBBO" in finazon["finding"]
    assert "macroeconomic context" in bea["finding"]
    assert finazon["live_quote"] is False
    assert bea["live_quote"] is False
    assert packet["soulaana_research"]["candidate_admitted"] is False
