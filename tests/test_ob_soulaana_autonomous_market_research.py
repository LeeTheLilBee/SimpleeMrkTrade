from types import SimpleNamespace
from datetime import datetime, timezone
import json

from tower.ob_soulaana_autonomous_market_research import (
    autonomous_dashboard_projection, resolve_credential,
)


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
        self.calls.append(request)
        payload = {}
        for i, symbol in enumerate(("AAPL","MSFT","NVDA","AMZN","GOOGL","META")):
            base = 100 + i * 5
            payload[symbol] = {
                "latestQuote": {
                    "bp": base + 1.0, "ap": base + 1.2,
                    "t": "2026-09-30T19:59:58Z"
                },
                "minuteBar": {
                    "c": base + 1.1, "v": 1000 + i * 100,
                    "t": "2026-09-30T19:59:00Z"
                },
                "dailyBar": {
                    "o": base - 1.0, "h": base + 3.0, "l": base - 2.0,
                    "c": base + 1.1, "v": 1000000 + i * 100000,
                    "t": "2026-09-30T13:30:00Z"
                },
                "prevDailyBar": {
                    "c": base - 3.0, "t": "2026-09-29T13:30:00Z"
                }
            }
        return Response(request.full_url, payload)


def temp_reader(_sid, provider):
    assert provider == "alpaca"
    return SimpleNamespace(
        key_id="PK_SYNTHETIC_12345",
        value="SK_SYNTHETIC_67890",
        probe="READ_ONLY_CHECK_PASSED",
    )


def test_temporary_credential_wins_over_hosted_env(monkeypatch):
    monkeypatch.setenv("OB_ALPACA_API_KEY_ID", "ENV_KEY")
    monkeypatch.setenv("OB_ALPACA_API_SECRET_KEY", "ENV_SECRET")
    item, source = resolve_credential(
        sid="tower_session_test_123456789",
        temp_reader=temp_reader,
    )
    assert source == "TEMPORARY_TOWER_SESSION"
    assert item.key_id == "PK_SYNTHETIC_12345"


def test_hosted_env_supports_continuous_operation(monkeypatch):
    monkeypatch.setenv("OB_ALPACA_API_KEY_ID", "ENV_KEY_12345")
    monkeypatch.setenv("OB_ALPACA_API_SECRET_KEY", "ENV_SECRET_67890")
    item, source = resolve_credential(sid=None, temp_reader=lambda *_: None)
    assert source == "HOSTED_ENV_SECRET"
    assert item.key_id == "ENV_KEY_12345"


def test_autonomous_scan_populates_dashboard_projection(monkeypatch):
    monkeypatch.setattr(
        "tower.ob_soulaana_autonomous_market_research.get_universe",
        lambda: ["AAPL","MSFT","NVDA","AMZN","GOOGL","META"],
    )
    packet = autonomous_dashboard_projection(
        sid="tower_session_test_123456789",
        temp_reader=temp_reader,
        opener=Recorder(),
        now=datetime(2026, 9, 30, 20, 0, tzinfo=timezone.utc),
    )
    assert packet["market_data_state"] == "source_bound_research_scan"
    assert packet["source"] == "alpaca-iex-owner-development"
    assert packet["projection_status"] == "fresh"
    assert len(packet["symbols"]) == 6
    assert len(packet["watchlist"]) <= 6
    assert len(packet["sectors"]) == 1
    assert packet["sectors"][0]["name"] == "Source-backed attention"
    assert len(packet["sectors"][0]["symbols"]) == 6
    assert all(row["source_coverage"] == ["alpaca"] for row in packet["symbols"])
    assert all("alpaca" in row["source_observations"] for row in packet["symbols"])
    assert packet["soulaana"]["headline"]
    assert packet["provider_boundary"]["sip_nbbo"] is False
    assert packet["tower_boundaries"]["no_order_submission"] is True
    assert packet["candidates"] == []
    assert packet["manual_live_queue"] == []
    assert "PK_SYNTHETIC" not in json.dumps(packet)
    assert "SK_SYNTHETIC" not in json.dumps(packet)
