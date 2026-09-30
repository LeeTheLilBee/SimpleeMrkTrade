"""Commercial-free market context: rights-bounded, quota-aware and non-execution."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from types import SimpleNamespace

from flask import Flask
import pytest

from engine.market_intake.commercial_free_market import (
    FINAZON_FREE_TRIAL_SYMBOLS,
    FINAZON_ID,
    TWELVE_DATA_ID,
    normalize_finazon_snapshot,
    normalize_twelve_data_quote,
    parse_finazon_ws_bar,
    parse_twelve_data_ws_price,
    stream_plan,
)
import tower.ob_commercial_free_market as runtime
from tower.ob_commercial_free_market import (
    PATH,
    CommercialFreeMarketService,
    create_commercial_free_market_status_blueprint,
)
from tower.ob_route_guard import match_ob_guard_policy
from tower.ob_web_route_enforcement import PROTECTED_EXACT_OB_ROUTES


SID = "tower_session_commercial_free_test_123456789"
NOW = datetime(2026, 9, 30, 14, 30, tzinfo=timezone.utc)
TwelveKey = SimpleNamespace(value="TWELVE_PRIVATE_TEST_KEY")
FinazonKey = SimpleNamespace(value="FINAZON_PRIVATE_TEST_KEY")


class Response:
    def __init__(self, url, payload, status=200):
        self.status = status
        self._url = url
        self._raw = json.dumps(payload).encode()

    def geturl(self):
        return self._url

    def read(self, limit):
        return self._raw[:limit]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class Recorder:
    def __init__(self):
        self.calls = []

    def open(self, request, timeout):
        self.calls.append((request, timeout))
        if "api.twelvedata.com/quote" in request.full_url:
            return Response(request.full_url, {
                "symbol": "AAPL",
                "timestamp": int((NOW - timedelta(seconds=2)).timestamp()),
                "open": "250.00", "high": "254.00", "low": "249.50",
                "close": "253.10", "previous_close": "249.25",
                "volume": "123456", "average_volume": "998877",
                "percent_change": "1.5446",
                "is_market_open": True,
                "fifty_two_week": {"high": "260.10", "low": "170.25"},
            })
        if "api.finazon.io/latest/finazon/us_stocks_essential/ticker_snapshot" in request.full_url:
            return Response(request.full_url, {
                "1d": {"o": 250.0, "h": 254.0, "l": 249.5, "c": 253.1, "v": 123456},
                "lt": {"p": 253.11, "s": 100, "tm": int((NOW - timedelta(seconds=1)).timestamp() * 1000)},
                "p1d": {"c": 249.25},
                "52w": {"h": 260.1, "l": 170.25, "av": 998877},
                "ch": {"dap": 1.55, "wep": 2.1, "mop": 4.25},
            })
        raise AssertionError("unexpected provider URL")


def secret_reader(_sid, provider):
    assert _sid == SID
    return {TWELVE_DATA_ID: TwelveKey, FINAZON_ID: FinazonKey}.get(provider)


def status_reader(_sid):
    assert _sid == SID
    return (
        {"id": "finnhub", "present": False, "probe": "NOT_CONFIGURED"},
        {"id": "alpha_vantage", "present": False, "probe": "NOT_CONFIGURED"},
        {"id": TWELVE_DATA_ID, "present": True, "probe": "READ_ONLY_CHECK_PASSED"},
        {"id": FINAZON_ID, "present": True, "probe": "READ_ONLY_CHECK_PASSED"},
    )


@pytest.fixture
def reviewed(monkeypatch):
    monkeypatch.setenv("OB_COMMERCIAL_FREE_MARKET_FETCH_ENABLED", "1")
    monkeypatch.setenv("OB_PROVIDER_TWELVE_DATA_BUSINESS_BASIC_REVIEWED", "1")
    monkeypatch.setenv("OB_PROVIDER_FINAZON_US_EQUITIES_BASIC_COMMERCIAL_REVIEWED", "1")
    monkeypatch.delenv("OB_PROVIDER_TWELVE_DATA_AI_USE_REVIEWED", raising=False)
    monkeypatch.delenv("OB_PROVIDER_FINAZON_AI_USE_REVIEWED", raising=False)
    monkeypatch.delenv("OB_PROVIDER_FINAZON_OWNER_DISPLAY_REVIEWED", raising=False)


def test_twelve_quote_normalizes_context_without_inventing_bid_ask():
    record = normalize_twelve_data_quote({
        "symbol": "AAPL",
        "timestamp": int((NOW - timedelta(seconds=1)).timestamp()),
        "open": "250", "high": "254", "low": "249", "close": "253",
        "previous_close": "249", "volume": "1234", "average_volume": "2000",
        "percent_change": "1.6064", "is_market_open": True,
        "fifty_two_week": {"high": "260", "low": "170"},
    }, symbol="AAPL", received_at=NOW)
    packet = record.internal_projection()
    assert record.source_id == TWELVE_DATA_ID
    assert record.last == 253
    assert record.volume == 1234
    assert packet["bid_ask_attached"] is False
    assert packet["execution_grade_quote"] is False
    assert packet["candidate_admitted"] is False
    assert "bid" not in packet and "ask" not in packet


def test_finazon_rich_snapshot_normalizes_free_trial_context():
    record = normalize_finazon_snapshot({
        "1d": {"o": 250, "h": 254, "l": 249, "c": 253, "v": 1234},
        "lt": {"p": 253.1, "s": 100,
               "tm": int((NOW - timedelta(seconds=1)).timestamp() * 1000)},
        "p1d": {"c": 249.0},
        "52w": {"h": 260, "l": 170, "av": 2000},
        "ch": {"dap": 1.6, "wep": 2.2, "mop": 4.4},
    }, symbol="AAPL", received_at=NOW)
    assert record.source_id == FINAZON_ID
    assert record.last == 253.1
    assert record.previous_close == 249.0
    assert record.weekly_change_percent == 2.2
    assert record.fifty_two_week_high == 260


def test_websocket_parsers_are_content_lanes_not_quote_authority():
    twelve = parse_twelve_data_ws_price({
        "event": "price", "symbol": "AAPL", "price": 253.1,
        "timestamp": int((NOW - timedelta(seconds=1)).timestamp()),
        "day_volume": 1234,
    }, received_at=NOW)
    finazon = parse_finazon_ws_bar({
        "t": int((NOW - timedelta(seconds=2)).timestamp()),
        "o": 250, "h": 254, "l": 249, "c": 253.1, "v": 1234,
    }, symbol="AAPL", received_at=NOW)
    for record in (twelve, finazon):
        packet = record.internal_projection()
        assert packet["execution_grade_quote"] is False
        assert packet["bid_ask_attached"] is False


def test_free_stream_plan_respects_real_free_slot_limits():
    plan = stream_plan(["MSFT", "AAPL", "TSLA", "NVDA", "GOOG", "META", "AMD", "SPY", "QQQ"])
    assert len(plan[TWELVE_DATA_ID]) == 8
    assert plan[TWELVE_DATA_ID][0] == "MSFT"
    assert len(plan[FINAZON_ID]) == 1
    assert plan[FINAZON_ID][0] == "AAPL"
    assert set(plan[FINAZON_ID]).issubset(FINAZON_FREE_TRIAL_SYMBOLS)


def test_default_off_or_missing_key_never_calls_provider(monkeypatch):
    rec = Recorder()
    service = CommercialFreeMarketService(
        secret_reader=lambda *_: None,
        status_reader=lambda *_: (),
        opener=rec,
        clock=lambda: NOW,
    )
    packet = service.read_symbol_internal(SID, "AAPL")
    assert rec.calls == []
    states = {row["provider"]: row["state"] for row in packet["provider_context"]}
    assert states[TWELVE_DATA_ID] == "NOT_CONFIGURED"
    assert states[FINAZON_ID] == "NOT_CONFIGURED"

    service = CommercialFreeMarketService(
        secret_reader=secret_reader,
        status_reader=status_reader,
        opener=rec,
        clock=lambda: NOW,
    )
    packet = service.read_symbol_internal(SID, "AAPL")
    assert rec.calls == []
    states = {row["provider"]: row["state"] for row in packet["provider_context"]}
    assert states[TWELVE_DATA_ID] == "RIGHTS_OR_FETCH_HOLD"
    assert states[FINAZON_ID] == "RIGHTS_OR_FETCH_HOLD"


def test_reviewed_internal_fetch_is_source_bound_cached_and_non_execution(reviewed):
    rec = Recorder()
    service = CommercialFreeMarketService(
        secret_reader=secret_reader, status_reader=status_reader,
        opener=rec, clock=lambda: NOW,
    )
    first = service.read_symbol_internal(SID, "AAPL")
    second = service.read_symbol_internal(SID, "AAPL")
    assert len(rec.calls) == 2  # one call per provider; second read is cached
    assert [x["state"] for x in first["provider_context"]] == ["SOURCE_BOUND", "SOURCE_BOUND"]
    assert second["digest"] == first["digest"]
    assert first["internal_non_display"] is True
    assert first["bid_ask_attached"] is False
    assert first["execution_grade_quote_attached"] is False
    assert first["candidate_admitted"] is False
    assert first["broker_execution_authorized"] is False
    assert first["capital_authorized"] is False
    assert first["may_change_trading_mode"] is False
    dumped = json.dumps(first)
    assert "TWELVE_PRIVATE_TEST_KEY" not in dumped
    assert "FINAZON_PRIVATE_TEST_KEY" not in dumped


def test_finazon_non_trial_symbol_holds_without_finazon_network(reviewed):
    rec = Recorder()
    service = CommercialFreeMarketService(
        secret_reader=secret_reader, status_reader=status_reader,
        opener=rec, clock=lambda: NOW,
    )
    packet = service.read_symbol_internal(SID, "MSFT")
    states = {row["provider"]: row["state"] for row in packet["provider_context"]}
    assert states[FINAZON_ID] == "TRIAL_SYMBOL_HOLD"
    assert sum("finazon.io" in req.full_url for req, _ in rec.calls) == 0
    assert sum("twelvedata.com" in req.full_url for req, _ in rec.calls) == 1


def test_status_projection_has_rights_and_limits_but_no_market_values(reviewed, monkeypatch):
    monkeypatch.setenv("OB_PROVIDER_FINAZON_OWNER_DISPLAY_REVIEWED", "1")
    service = CommercialFreeMarketService(
        secret_reader=secret_reader, status_reader=status_reader,
        opener=Recorder(), clock=lambda: NOW,
    )
    status = service.status(SID)
    dumped = json.dumps(status)
    assert status["schema"] == "OB_COMMERCIAL_FREE_MARKET_STATUS_V1"
    assert status["raw_market_values_attached"] is False
    assert status["browser_display_authority"] is False
    providers = {x["provider"]: x for x in status["providers"]}
    assert providers[TWELVE_DATA_ID]["commercial_internal_use"] is True
    assert providers[TWELVE_DATA_ID]["owner_display"] is False
    assert providers[FINAZON_ID]["owner_display"] is True
    assert providers[TWELVE_DATA_ID]["stream_slots"] == 8
    assert providers[FINAZON_ID]["stream_slots"] == 1
    for forbidden in ("253.1", "123456", "TWELVE_PRIVATE_TEST_KEY", "FINAZON_PRIVATE_TEST_KEY"):
        assert forbidden not in dumped


def test_status_route_is_exact_owner_only_and_get_only(reviewed, monkeypatch):
    gate = {"owner": False}
    service = CommercialFreeMarketService(
        secret_reader=secret_reader, status_reader=status_reader,
        opener=Recorder(), clock=lambda: NOW,
    )
    app = Flask(__name__)
    app.secret_key = "commercial-free-test-only"
    app.register_blueprint(create_commercial_free_market_status_blueprint(
        owner_authorize=lambda: gate["owner"], service=service
    ))
    client = app.test_client()
    with client.session_transaction() as session:
        session["tower_session_id"] = SID
    assert client.get(PATH).status_code == 403
    gate["owner"] = True
    response = client.get(PATH)
    assert response.status_code == 200
    assert response.get_json()["raw_market_values_attached"] is False
    assert client.post(PATH).status_code == 405
    assert PATH in PROTECTED_EXACT_OB_ROUTES
    assert match_ob_guard_policy(PATH)["match_type"] == "exact"
    assert match_ob_guard_policy(PATH + "/raw")["match_type"] == "unmapped_default_deny"
