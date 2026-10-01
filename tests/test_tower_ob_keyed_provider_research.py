"""Offline tests for authenticated keyed-provider research dissemination.

No real provider traffic, credentials, quotes or broker calls.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

from flask import Flask
import pytest

from engine.market_intake.observatory_event_stream import ObservatoryEventHub
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
            if "function=OVERVIEW" in request.full_url:
                return Response(request.full_url, {
                    "Symbol": "AAPL",
                    "AssetType": "Common Stock",
                    "Name": "Apple Inc",
                    "Description": "Apple designs, manufactures and markets smartphones, personal computers, tablets, wearables and services.",
                    "CIK": "0000320193",
                    "Exchange": "NASDAQ",
                    "Currency": "USD",
                    "Country": "USA",
                    "Sector": "TECHNOLOGY",
                    "Industry": "CONSUMER ELECTRONICS",
                    "Address": "One Apple Park Way, Cupertino, CA",
                    "FiscalYearEnd": "September",
                    "LatestQuarter": "2026-06-30",
                    "MarketCapitalization": "3200000000000",
                    "SharesOutstanding": "15000000000",
                    "RevenueTTM": "420000000000",
                    "EPS": "7.20",
                    "PERatio": "34.5",
                    "ProfitMargin": "0.255",
                    "Beta": "1.18",
                    "52WeekHigh": "260.10",
                    "52WeekLow": "170.20"
                })
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
        if "data.alpaca.markets/v2/stocks/AAPL/quotes/latest" in request.full_url:
            return Response(request.full_url, {
                "quote": {"bp": 100.0, "bs": 10, "ap": 100.2, "as": 12,
                          "t": "2026-09-30T19:00:00Z"}
            })
        if "data.alpaca.markets/v2/stocks/AAPL/bars/latest" in request.full_url:
            return Response(request.full_url, {
                "bar": {"o": 99.0, "h": 101.0, "l": 98.5, "c": 100.1,
                        "v": 12345, "t": "2026-09-30T19:00:00Z"}
            })
        if "apps.bea.gov/api/data" in request.full_url:
            values = {
                "T10105": ("31,250.0", "30,900.0"),
                "T10106": ("23,000.0", "22,800.0"),
                "T10101": ("3.8", "2.9"),
                "T10107": ("2.6", "3.1"),
            }
            table = next((name for name in values if "TableName=" + name in request.full_url), None)
            if table is None:
                raise AssertionError("unexpected BEA table")
            latest, prior = values[table]
            return Response(request.full_url, {
                "BEAAPI": {"Results": {"Data": [
                    {"LineNumber": "1", "TimePeriod": "2026Q2", "DataValue": latest},
                    {"LineNumber": "1", "TimePeriod": "2026Q1", "DataValue": prior},
                    {"LineNumber": "2", "TimePeriod": "2026Q2", "DataValue": "999"},
                ]}}
            })
        raise AssertionError("unexpected URL")


def secret_reader(sid, provider):
    assert sid.startswith("tower_session_")
    if provider == "alpaca":
        return SimpleNamespace(
            value="SECRET-alpaca", key_id="KEY-alpaca-123", probe="READ_ONLY_CHECK_PASSED"
        )
    return SimpleNamespace(value="SECRET-" + provider, probe="READ_ONLY_CHECK_PASSED")


@pytest.fixture
def rights(monkeypatch):
    monkeypatch.setenv("OB_PROVIDER_RESEARCH_FETCH_ENABLED", "1")
    for provider in ("FINNHUB", "ALPHA_VANTAGE", "FINAZON", "ALPACA", "BEA"):
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
    assert [x["state"] for x in packet["provider_research"]] == ["NOT_CONNECTED"] * 5
    assert packet["soulaana_research"]["observations"] == []


def test_rights_hold_never_calls_provider(monkeypatch):
    monkeypatch.delenv("OB_PROVIDER_RESEARCH_FETCH_ENABLED", raising=False)
    rec = Recorder()
    packet = provider_research_projection(
        sid="tower_session_" + "x"*20, symbol="AAPL",
        secret_reader=secret_reader, opener=rec, cache=ProviderResearchCache())
    assert not rec.calls
    assert [x["state"] for x in packet["provider_research"]] == ["RIGHTS_OR_FETCH_HOLD"]*5


def test_source_bound_owner_projection_is_bounded_and_not_live(rights):
    rec = Recorder()
    packet = provider_research_projection(
        sid="tower_session_" + "x"*20, symbol="AAPL",
        secret_reader=secret_reader, opener=rec, cache=ProviderResearchCache())
    assert len(rec.calls) == 10
    assert packet["schema"] == "OB_KEYED_PROVIDER_RESEARCH_V1"
    assert packet["live_prices_attached"] is True
    assert packet["orders_attached"] is False
    assert packet["may_authorize_order"] is False
    finnhub, alpha, finazon, alpaca, bea = packet["provider_research"]
    assert finnhub["state"] == "SOURCE_BOUND"
    assert finnhub["security_name"] == "Apple Inc"
    assert "marketCapitalization" not in finnhub
    assert alpha["state"] == "SOURCE_BOUND"
    assert alpha["historical_only"] is False
    assert len(alpha["bars"]) == 3
    assert alpha["company_profile"]["name"] == "Apple Inc"
    assert alpha["company_profile"]["sector"] == "TECHNOLOGY"
    assert alpha["company_profile"]["industry"] == "CONSUMER ELECTRONICS"
    assert "smartphones" in alpha["company_profile"]["description"]
    assert alpha["company_profile"]["market_cap"] == 3200000000000.0
    assert alpha["personal_owner_only"] is True
    assert alpha["commercial_or_beta_use_allowed"] is False
    assert alpha["bars"][0]["session_date"] == "2026-09-28"
    assert finazon["state"] == "SOURCE_BOUND"
    assert finazon["real_time_market_context"] is True
    assert finazon["consolidated_quote"] is False
    assert alpaca["state"] == "SOURCE_BOUND"
    assert alpaca["provider"] == "alpaca"
    assert alpaca["feed"] == "iex"
    assert alpaca["quote"]["midpoint"] == 100.1
    assert alpaca["consolidated_quote"] is False
    assert bea["state"] == "SOURCE_BOUND"
    assert bea["kind"] == "OFFICIAL_US_QUARTERLY_MACRO_CONTEXT"
    assert bea["unit"] == "BILLIONS_OF_CURRENT_DOLLARS_SAAR"
    assert bea["observations"][0] == {"period": "2026Q2", "value": "31250.0"}
    assert [x["series_id"] for x in bea["macro_series"]] == [
        "nominal_gdp", "real_gdp", "real_gdp_growth", "gdp_price_change"]
    growth = next(x for x in bea["macro_series"] if x["series_id"] == "real_gdp_growth")
    prices = next(x for x in bea["macro_series"] if x["series_id"] == "gdp_price_change")
    assert growth["observations"][0]["value"] == "3.8"
    assert prices["observations"][0]["value"] == "2.6"
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
    assert history["source_reference"] == "https://www.alphavantage.co/documentation/"
    assert "Apple Inc" in history["finding"]
    assert "CONSUMER ELECTRONICS" in history["finding"]
    assert history["why_it_matters"]
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
    assert len(recorder.calls) == 10  # no fresh provider call needed
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

def test_cache_snapshot_for_symbol_reuses_only_existing_rows_without_network(rights):
    rec = Recorder()
    cache = ProviderResearchCache()
    sid = "tower_session_" + "x"*20
    assert cache.snapshot_for_symbol(sid, "AAPL") == []
    packet = provider_research_projection(
        sid=sid, symbol="AAPL",
        secret_reader=secret_reader, opener=rec, cache=cache)
    before = len(rec.calls)
    rows = cache.snapshot_for_symbol(sid, "AAPL")
    assert len(rec.calls) == before
    assert {row["provider"] for row in rows} == {
        "finnhub", "alpha_vantage", "finazon", "alpaca", "bea"
    }
    assert all(row["state"] == "SOURCE_BOUND" for row in rows)
    assert cache.snapshot_for_symbol(sid, "MSFT") == []
    assert packet["symbol"] == "AAPL"


def test_cache_avoids_repeat_provider_call_within_ttl(rights):
    rec = Recorder()
    cache = ProviderResearchCache()
    args = dict(sid="tower_session_"+"x"*20, symbol="AAPL",
                secret_reader=secret_reader, opener=rec, cache=cache)
    first = provider_research_projection(**args)
    second = provider_research_projection(**args)
    assert len(rec.calls) == 10
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


def test_http_provider_research_records_truthful_soulaana_event_receipts(rights, monkeypatch):
    monkeypatch.setenv("OB_PROVIDER_FINNHUB_AI_USE_REVIEWED", "1")
    hub = ObservatoryEventHub()
    app = Flask(__name__)
    app.secret_key = "test-only"
    app.config["TESTING"] = True
    app.register_blueprint(create_keyed_provider_research_blueprint(
        owner_authorize=lambda: True,
        secret_reader=secret_reader,
        opener=Recorder(),
        event_hub=hub,
    ))
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["tower_session_id"] = "tower_session_" + "x"*20

    response = client.get(PATH + "?symbol=AAPL")
    assert response.status_code == 200

    traces = hub.trace_snapshot()["traces"]
    assert len(traces) == 1
    trace = traces[0]
    assert trace["source"] == "keyed_provider_research"
    assert trace["symbol"] == "AAPL"
    assert trace["stages"]["RECEIVED"] is True
    assert trace["stages"]["VALIDATED"] is True
    assert trace["stages"]["NORMALIZED"] is True
    assert trace["stages"]["PUBLISHED"] is True
    assert trace["stages"]["SCANNER_CONSUMED"] is False
    assert trace["stages"]["SOULAANA_CONSUMED"] is True
    assert trace["stages"]["SOULAANA_INTERPRETED"] is True
    assert trace["soulaana_complete"] is True

    # Same cached research content must not manufacture a second event/receipt.
    second = client.get(PATH + "?symbol=AAPL")
    assert second.status_code == 200
    assert len(hub.trace_snapshot()["traces"]) == 1


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
    assert "real GDP growth" in observations[1]["finding"]
    assert observations[1]["why_it_matters"]
    assert observations[1]["what_would_confirm"]
    assert observations[1]["what_would_conflict"]
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
    assert "real GDP growth" in bea["finding"]
    assert "growth" in bea["why_it_matters"].lower()
    assert finazon["live_quote"] is False
    assert bea["live_quote"] is False
    assert packet["soulaana_research"]["candidate_admitted"] is False


def test_public_personal_quote_can_feed_owner_soulaana_without_order_authority(rights):
    def public_reader(sid, symbol, kind):
        assert sid.startswith("tower_session_")
        assert symbol == "AAPL"
        assert kind == "EQUITY"
        return {
            "provider": "public",
            "state": "SOURCE_BOUND",
            "kind": "PUBLIC_PERSONAL_REALTIME_QUOTE",
            "symbol": symbol,
            "bid": 100.0,
            "ask": 100.2,
            "last": 100.1,
            "observed_at": "2026-10-01T14:00:00Z",
            "source_reference": "https://public.com/api/docs/resources/market-data/get-quotes",
            "historical_only": False,
            "live_quote": False,
            "real_time_market_context": True,
            "consolidated_quote": False,
            "personal_owner_only": True,
            "commercial_use_allowed": False,
            "beta_user_use_allowed": False,
            "broker_execution_authorized": False,
            "owner_display_reviewed": True,
            "soulaana_ai_use_reviewed": True,
        }

    packet = provider_research_projection(
        sid="tower_session_" + "x"*20,
        symbol="AAPL",
        secret_reader=secret_reader,
        public_reader=public_reader,
        opener=Recorder(),
        cache=ProviderResearchCache(),
    )
    public_row = next(row for row in packet["provider_research"]
                      if row.get("provider") == "public")
    assert public_row["state"] == "SOURCE_BOUND"
    assert public_row["personal_owner_only"] is True
    assert public_row["commercial_use_allowed"] is False
    assert public_row["broker_execution_authorized"] is False
    observations = packet["soulaana_research"]["observations"]
    public_ai = next(row for row in observations if row["provider"] == "public")
    assert "Public reports owner-only personal market context" in public_ai["finding"]
    assert public_ai["summary"]["bid"] == 100.0
    assert packet["may_authorize_order"] is False
    assert packet["may_authorize_capital"] is False


def test_soulaana_fuses_all_ai_approved_sources_without_selecting_one(rights, monkeypatch):
    for provider in ("FINNHUB", "ALPHA_VANTAGE", "FINAZON", "ALPACA", "BEA"):
        monkeypatch.setenv(f"OB_PROVIDER_{provider}_AI_USE_REVIEWED", "1")

    def public_reader(sid, symbol, kind):
        return {
            "provider": "public",
            "state": "SOURCE_BOUND",
            "kind": "PUBLIC_PERSONAL_REALTIME_QUOTE",
            "symbol": symbol,
            "bid": 100.1,
            "ask": 100.3,
            "last": 100.2,
            "observed_at": "2026-10-01T14:00:00Z",
            "source_reference": "https://public.com/api/docs/resources/market-data/get-quotes",
            "historical_only": False,
            "live_quote": False,
            "real_time_market_context": True,
            "consolidated_quote": False,
            "personal_owner_only": True,
            "commercial_use_allowed": False,
            "beta_user_use_allowed": False,
            "broker_execution_authorized": False,
            "owner_display_reviewed": True,
            "soulaana_ai_use_reviewed": True,
        }

    packet = provider_research_projection(
        sid="tower_session_" + "x"*20,
        symbol="AAPL",
        secret_reader=secret_reader,
        public_reader=public_reader,
        opener=Recorder(),
        cache=ProviderResearchCache(),
    )
    fusion = packet["soulaana_research"]["fusion"]
    assert fusion["schema"] == "OB_SOULAANA_MULTI_SOURCE_FUSION_V1"
    assert set(fusion["consumed_providers"]) == {
        "finnhub", "alpha_vantage", "finazon", "alpaca", "bea", "public"
    }
    assert set(fusion["eligible_source_bound_providers"]) == set(fusion["consumed_providers"])
    assert fusion["all_eligible_source_bound_consumed"] is True
    assert set(fusion["source_families"]["current_market"]) == {"finazon", "alpaca", "public"}
    assert fusion["current_market_comparison"]["source_count"] == 3
    assert fusion["current_market_comparison"]["winner_selected"] is False
    assert fusion["single_provider_selected_as_truth"] is False
    assert fusion["cross_source_causality_claimed"] is False
    assert packet["may_authorize_order"] is False
    assert packet["may_authorize_capital"] is False


def test_public_options_setting_controls_fetch_and_soulaana_translation(rights):
    calls = []

    def option_reader(sid, symbol):
        calls.append((sid, symbol))
        return {
            "provider": "public_options",
            "state": "SOURCE_BOUND",
            "kind": "PUBLIC_PERSONAL_OPTION_CHAIN",
            "symbol": symbol,
            "expiration": "2026-10-02",
            "underlying_midpoint": 100.3,
            "contract_count": 2,
            "contracts": [
                {
                    "provider_symbol": "AAPL261002C00100000",
                    "right": "call", "strike": 100.0,
                    "bid": 1.2, "ask": 1.3, "mid": 1.25,
                    "volume": 100, "open_interest": 900,
                    "greeks": {"delta": 0.52, "implied_volatility": 0.31},
                },
                {
                    "provider_symbol": "AAPL261002P00100000",
                    "right": "put", "strike": 100.0,
                    "bid": 1.1, "ask": 1.25, "mid": 1.175,
                    "volume": 90, "open_interest": 800,
                    "greeks": {"delta": -0.48, "implied_volatility": 0.33},
                },
            ],
            "source_reference": "https://public.com/api/docs/resources/market-data/get-option-chain",
            "owner_display_reviewed": True,
            "soulaana_ai_use_reviewed": True,
            "personal_owner_only": True,
            "commercial_use_allowed": False,
            "broker_execution_authorized": False,
        }

    enabled = provider_research_projection(
        sid="tower_session_" + "x"*20,
        symbol="AAPL",
        secret_reader=secret_reader,
        public_option_reader=option_reader,
        use_public_options=True,
        opener=Recorder(),
        cache=ProviderResearchCache(),
    )
    assert len(calls) == 1
    option_row = next(row for row in enabled["provider_research"]
                      if row.get("provider") == "public_options")
    assert option_row["state"] == "SOURCE_BOUND"
    ai = next(row for row in enabled["soulaana_research"]["observations"]
              if row.get("provider") == "public_options")
    assert "options chain" in ai["finding"]
    assert ai["why_it_matters"]
    assert enabled["may_authorize_order"] is False

    calls.clear()
    disabled = provider_research_projection(
        sid="tower_session_" + "x"*20,
        symbol="AAPL",
        secret_reader=secret_reader,
        public_option_reader=option_reader,
        use_public_options=False,
        opener=Recorder(),
        cache=ProviderResearchCache(),
    )
    assert calls == []
    held = next(row for row in disabled["provider_research"]
                if row.get("provider") == "public_options")
    assert held["state"] == "DISABLED_BY_OWNER"
    assert not any(row.get("provider") == "public_options"
                   for row in disabled["soulaana_research"]["observations"])
