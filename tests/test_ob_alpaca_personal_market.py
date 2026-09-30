from tower.ob_provider_key_desk import TemporaryProviderKeyStore, PROVIDERS
from tower.ob_alpaca_personal_market import latest_stock_context, websocket_plan


class _Resp:
    status = 200
    def __init__(self, url, payload):
        self._url = url
        self._payload = payload
    def geturl(self):
        return self._url
    def read(self, _limit):
        import json
        return json.dumps(self._payload).encode("utf-8")
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False


class _Opener:
    def open(self, req, timeout=8):
        assert req.headers.get("Apca-api-key-id") == "PKTEST123456"
        assert req.headers.get("Apca-api-secret-key") == "SECRET123456789"
        if "/quotes/latest" in req.full_url:
            payload = {"quote": {"bp": 100.0, "bs": 10, "ap": 100.2, "as": 12, "t": "2026-09-30T19:00:00Z"}}
        else:
            payload = {"bar": {"o": 99.0, "h": 101.0, "l": 98.5, "c": 100.1, "v": 12345, "t": "2026-09-30T19:00:00Z"}}
        return _Resp(req.full_url, payload)


def test_alpaca_is_registered_as_pair_provider():
    assert "alpaca" in PROVIDERS
    assert PROVIDERS["alpaca"]["credential_pair"] is True


def test_temporary_store_keeps_alpaca_pair_server_side():
    store = TemporaryProviderKeyStore()
    sid = "tower_session_test"
    store.put(sid, "alpaca", "SECRET123456789", key_id="PKTEST123456")
    item = store.get(sid, "alpaca")
    assert item.value == "SECRET123456789"
    assert item.key_id == "PKTEST123456"
    status = {row["id"]: row for row in store.status(sid)}
    assert status["alpaca"]["present"] is True
    assert "SECRET" not in repr(status)
    assert "PKTEST" not in repr(status)


def test_alpaca_latest_context_is_non_execution_owner_development():
    store = TemporaryProviderKeyStore()
    sid = "tower_session_test"
    store.put(sid, "alpaca", "SECRET123456789", key_id="PKTEST123456")
    out = latest_stock_context("AAPL", item=store.get(sid, "alpaca"), opener=_Opener())
    assert out["provider"] == "alpaca"
    assert out["feed"] == "iex"
    assert out["latest_quote"]["midpoint"] == 100.1
    assert out["latest_minute_bar"]["close"] == 100.1
    assert out["rights"]["account_scope"] == "PERSONAL_OWNER_DEVELOPMENT"
    assert out["execution_grade_quote"] is False
    assert out["broker_execution_authorized"] is False
    assert out["capital_authorized"] is False


def test_alpaca_stream_plan_is_declarative_only():
    plan = websocket_plan()
    assert plan["endpoint"].endswith("/v2/iex")
    assert set(plan["channels"]) == {"trades", "quotes", "bars"}
    assert plan["commercial_rights_inferred"] is False
    assert plan["execution_authority"] is False
