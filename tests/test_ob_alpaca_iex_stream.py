from tower.ob_alpaca_iex_stream import AlpacaIEXStreamManager, ENDPOINT


def test_alpaca_stream_contract_is_read_only_and_iex():
    manager = AlpacaIEXStreamManager()
    status = manager.status()
    assert ENDPOINT == "wss://stream.data.alpaca.markets/v2/iex"
    assert status["read_only"] is True
    assert status["provider_payload_exposed_to_browser"] is False
    assert status["broker_execution_authorized"] is False
    assert status["capital_authorized"] is False
    assert status["candidate_admitted"] is False
    assert status["may_change_trading_mode"] is False


def test_alpaca_stream_normalizes_quote_trade_and_bar_without_authority():
    manager = AlpacaIEXStreamManager()
    quote = manager._normalize("q", "AAPL", {
        "T": "q", "S": "AAPL", "bp": 100.0, "bs": 2,
        "ap": 100.2, "as": 3, "t": "2026-10-01T00:30:00Z",
    })
    trade = manager._normalize("t", "AAPL", {
        "T": "t", "S": "AAPL", "p": 100.1, "s": 5,
        "t": "2026-10-01T00:30:01Z",
    })
    bar = manager._normalize("b", "AAPL", {
        "T": "b", "S": "AAPL", "o": 99.8, "h": 100.3,
        "l": 99.7, "c": 100.1, "v": 4000, "n": 120,
        "vw": 100.04, "t": "2026-10-01T00:30:00Z",
    })
    assert quote["midpoint"] == 100.1
    assert quote["execution_grade_quote"] is False
    assert trade["price"] == 100.1
    assert bar["close"] == 100.1
    for row in (quote, trade, bar):
        assert row["provider"] == "alpaca"
        assert row["feed"] == "iex"
        assert row["candidate_admitted"] is False
        assert row["broker_execution_authorized"] is False


def test_alpaca_stream_auth_success_shape():
    manager = AlpacaIEXStreamManager()
    assert manager._auth_ok([
        {"T": "success", "msg": "connected"},
        {"T": "success", "msg": "authenticated"},
    ]) is True
    assert manager._auth_ok([{"T": "error", "msg": "auth failed"}]) is False
