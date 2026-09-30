"""Owner API-key Desk: sealed credential handling, exact routes, no live admission."""
from datetime import timedelta
from pathlib import Path

import pytest
from flask import Flask, render_template

import tower.ob_provider_key_desk as desk
from tower.ob_route_guard import match_ob_guard_policy
from tower.ob_web_route_enforcement import PROTECTED_EXACT_OB_ROUTES, is_approved_ob_web_room

HERE = Path(__file__).resolve().parents[1]


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("OB_PROVIDER_KEY_DESK_ENABLED", "1")
    monkeypatch.setattr(desk, "_approved_browser_origin", lambda: "https://tower.example")
    gate = {"owner": False}
    calls = []
    memory = desk.TemporaryProviderKeyStore()
    app = Flask(__name__, template_folder=str(HERE / "web/templates"),
                static_folder=str(HERE / "web/static"))
    app.secret_key = "synthetic-test-only-not-a-live-session"
    app.register_blueprint(desk.create_provider_key_blueprint(
        owner_authorize=lambda: gate["owner"],
        store=memory,
        probe=lambda provider, key: calls.append((provider, key)) or "READ_ONLY_CHECK_PASSED",
    ))
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["tower_session_id"] = "tower_session_synthetic_only_123456789"
    return app, client, gate, memory, calls


def csrf(client):
    with client.session_transaction() as sess:
        return sess["ob_provider_key_csrf"]


def send(client, provider="finnhub", operation="save", secret="VERY_PRIVATE_SYNTHETIC_TEST_TOKEN", **extra):
    fields = {"csrf": csrf(client), "provider": provider, "operation": operation}
    if operation == "save":
        fields["secret"] = secret
    return client.post(desk.PATH, data=fields, headers={
        "Origin": "https://tower.example", "Sec-Fetch-Site": "same-origin"}, **extra)


def test_owner_only_get_does_not_create_source_or_make_provider_calls(env):
    app, client, gate, memory, calls = env
    assert client.get(desk.PATH).status_code == 403
    gate["owner"] = True
    page = client.get(desk.PATH)
    assert page.status_code == 200
    assert b"Finnhub" in page.data and b"Alpha Vantage" in page.data
    assert b"Twelve Data" in page.data and b"Finazon" in page.data and b"Alpaca" in page.data
    assert b"SEC EDGAR" in page.data and b"Public" in page.data
    assert calls == []
    assert memory.status("tower_session_synthetic_only_123456789")[0]["present"] is False
    assert desk.PATH in PROTECTED_EXACT_OB_ROUTES
    assert is_approved_ob_web_room(desk.PATH) is True
    assert match_ob_guard_policy(desk.PATH)["match_type"] != "unmapped_default_deny"
    assert is_approved_ob_web_room(desk.PATH + "/connect") is False
    assert app.extensions.get("ob_provider_key_desk_v1") is None  # this test uses only the blueprint


def test_save_verify_forget_no_key_in_html_or_cookie(env):
    _, client, gate, memory, calls = env
    gate["owner"] = True
    client.get(desk.PATH)
    raw = "VERY_PRIVATE_SYNTHETIC_TEST_TOKEN"
    result = send(client, secret=raw)
    assert result.status_code == 303
    assert raw.encode() not in result.data
    page = client.get(desk.PATH)
    assert raw.encode() not in page.data
    assert b"NOT TESTED" in page.data
    assert b"Diagnostic:" in page.data
    assert b"Credential is present but has not been verified yet." in page.data
    with client.session_transaction() as sess:
        assert raw not in str(dict(sess))
    result = send(client, operation="verify")
    assert result.status_code == 303
    assert calls == [("finnhub", raw)]
    assert b"READ ONLY CHECK PASSED" in client.get(desk.PATH).data
    # One provider credential cannot give the other provider a successful state.
    assert memory.get("tower_session_synthetic_only_123456789", "alpha_vantage") is None
    assert send(client, operation="verify").status_code == 303
    assert len(calls) == 1  # cooldown
    assert send(client, operation="forget").status_code == 303
    assert raw.encode() not in client.get(desk.PATH).data
    assert memory.get("tower_session_synthetic_only_123456789", "finnhub") is None


def test_provider_slots_are_independent(env):
    _, client, gate, memory, _ = env
    gate["owner"] = True
    client.get(desk.PATH)
    providers = ("finnhub", "alpha_vantage", "twelve_data", "finazon")
    for index, provider in enumerate(providers):
        secret = f"PRIVATE_SYNTHETIC_KEY_{index}_ABCDEFG"
        assert send(client, provider=provider, secret=secret).status_code == 303
        item = memory.get("tower_session_synthetic_only_123456789", provider)
        assert item is not None and item.value == secret
    statuses = memory.status("tower_session_synthetic_only_123456789")
    assert len(statuses) == 5
    by_id = {row["id"]: row for row in statuses}
    assert all(by_id[p]["present"] for p in providers)
    assert by_id["alpaca"]["present"] is False
    assert all("value" not in row and "secret" not in row and "key_id" not in row for row in statuses)


def test_each_vendor_uses_independent_slot_and_expires(env):
    _, client, gate, memory, _ = env
    gate["owner"] = True
    client.get(desk.PATH)
    assert send(client, provider="alpha_vantage", secret="ALPHA_SYNTHETIC_SECRET").status_code == 303
    assert memory.get("tower_session_synthetic_only_123456789", "alpha_vantage") is not None
    item = memory.get("tower_session_synthetic_only_123456789", "alpha_vantage")
    item.expires_at = desk._now() - timedelta(seconds=1)
    assert memory.get("tower_session_synthetic_only_123456789", "alpha_vantage") is None


@pytest.mark.parametrize("origin,site", [
    ("null", "same-origin"), ("https://evil.example", "same-origin"),
    ("http://tower.example", "same-origin"), ("", ""), ("", "same-site"),
    ("https://tower.example", "cross-site"),
])
def test_origin_and_fetch_metadata_rejected_before_secret_entry(env, origin, site):
    _, client, gate, memory, _ = env
    gate["owner"] = True
    client.get(desk.PATH)
    result = client.post(desk.PATH, data={
        "csrf": csrf(client), "provider": "finnhub", "operation": "save",
        "secret": "VERY_PRIVATE_SYNTHETIC_TEST_TOKEN",
    }, headers={"Origin": origin, "Sec-Fetch-Site": site})
    assert result.status_code == 403
    assert b"VERY_PRIVATE_SYNTHETIC_TEST_TOKEN" not in result.data
    assert memory.get("tower_session_synthetic_only_123456789", "finnhub") is None


def test_csrf_feature_flag_and_unmapped_provider_are_separate_holds(env, monkeypatch):
    _, client, gate, memory, calls = env
    gate["owner"] = True
    client.get(desk.PATH)
    bad = client.post(desk.PATH, data={"csrf": "wrong", "provider": "finnhub",
                                      "operation": "save", "secret": "PRIVATE_TEST_TOKEN"},
                      headers={"Origin": "https://tower.example", "Sec-Fetch-Site": "same-origin"})
    assert bad.status_code == 403
    monkeypatch.setenv("OB_PROVIDER_KEY_DESK_ENABLED", "0")
    assert send(client).status_code == 403
    monkeypatch.setenv("OB_PROVIDER_KEY_DESK_ENABLED", "1")
    assert send(client, provider="https://untrusted.example").status_code == 400
    assert memory.get("tower_session_synthetic_only_123456789", "finnhub") is None
    assert calls == []


def test_keys_cannot_be_rendered_and_never_prove_market_or_trade_rights(env):
    _, client, gate, memory, _ = env
    gate["owner"] = True
    client.get(desk.PATH)
    assert send(client, secret="PRIVATE_TEST_TOKEN").status_code == 303
    statuses = memory.status("tower_session_synthetic_only_123456789")
    assert all("value" not in p and "secret" not in p for p in statuses)
    assert "PRIVATE_TEST_TOKEN" not in repr(statuses)
    with pytest.raises(ValueError):
        desk.probe_one("unlisted_provider", "any-key")


class _FakeResponse:
    def __init__(self, payload):
        import json
        self.status = 200
        self.headers = {"Content-Type": "application/json"}
        self.payload = json.dumps(payload).encode()
        self.url = ""
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, count): return self.payload[:count]
    def geturl(self): return self.url


class _FakeOpener:
    def __init__(self, payload):
        self.payload = payload
        self.requests = []
    def open(self, request, timeout):
        self.requests.append(request)
        response = _FakeResponse(self.payload)
        response.url = request.full_url
        return response


def test_fixed_official_probe_endpoints_and_sanitized_response():
    finn = _FakeOpener({"ticker": "AAPL", "name": "Apple Inc."})
    assert desk.probe_one("finnhub", "PRIVATE_FINNHUB_TEST", opener=finn) == "READ_ONLY_CHECK_PASSED"
    assert finn.requests[0].full_url == "https://finnhub.io/api/v1/stock/profile2?symbol=AAPL"
    assert finn.requests[0].get_header("X-finnhub-token") == "PRIVATE_FINNHUB_TEST"
    assert "PRIVATE_FINNHUB_TEST" not in finn.requests[0].full_url
    alpha = _FakeOpener({"Meta Data": {}, "Time Series (Daily)": {"2026-09-28": {}}})
    assert desk.probe_one("alpha_vantage", "PRIVATE_ALPHA_TEST", opener=alpha) == "READ_ONLY_CHECK_PASSED"
    assert alpha.requests[0].full_url.startswith("https://www.alphavantage.co/query?")
    assert "outputsize=compact" in alpha.requests[0].full_url
    limited = _FakeOpener({"Information": "Thank you. Standard API rate limit is 25 requests per day."})
    assert desk.probe_one("alpha_vantage", "PRIVATE_ALPHA_TEST", opener=limited) == "RATE_LIMITED"
    rejected = _FakeOpener({"Information": "Invalid API key. Please check your API key."})
    assert desk.probe_one("alpha_vantage", "PRIVATE_ALPHA_TEST", opener=rejected) == "ACCESS_REJECTED"
    provider_message = _FakeOpener({"Information": "Scheduled maintenance notice"})
    assert desk.probe_one("alpha_vantage", "PRIVATE_ALPHA_TEST", opener=provider_message) == "PROVIDER_MESSAGE"
    malformed = _FakeOpener({"unexpected": True})
    assert desk.probe_one("alpha_vantage", "PRIVATE_ALPHA_TEST", opener=malformed) == "RESPONSE_SHAPE_HOLD"

    twelve = _FakeOpener({
        "symbol": "AAPL", "timestamp": 1780240000, "close": "250.00"
    })
    assert desk.probe_one("twelve_data", "PRIVATE_TWELVE_TEST", opener=twelve) == "READ_ONLY_CHECK_PASSED"
    assert twelve.requests[0].full_url == "https://api.twelvedata.com/quote?symbol=AAPL"
    assert twelve.requests[0].get_header("Authorization") == "apikey PRIVATE_TWELVE_TEST"
    assert "PRIVATE_TWELVE_TEST" not in twelve.requests[0].full_url

    finazon = _FakeOpener({
        "1d": {"c": 250}, "lt": {"p": 250.1, "tm": 1780240000000},
        "52w": {"h": 260, "l": 170, "av": 1000},
        "ch": {"dap": 1}, "p1d": {"c": 248}
    })
    assert desk.probe_one("finazon", "PRIVATE_FINAZON_TEST", opener=finazon) == "READ_ONLY_CHECK_PASSED"
    assert finazon.requests[0].full_url == (
        "https://api.finazon.io/latest/finazon/us_stocks_essential/ticker_snapshot?ticker=AAPL"
    )
    assert finazon.requests[0].get_header("Authorization") == "apikey PRIVATE_FINAZON_TEST"
    assert "PRIVATE_FINAZON_TEST" not in finazon.requests[0].full_url

    with pytest.raises(ValueError):
        desk.probe_one("custom-url", "PRIVATE_ALPHA_TEST", opener=alpha)
