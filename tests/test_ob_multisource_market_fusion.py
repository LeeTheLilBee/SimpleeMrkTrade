from types import SimpleNamespace

from tower.ob_market_source_status import _merge_public_owner_context


def base_document():
    rows = [
        {
            "symbol": "AAPL",
            "source": "Alpaca IEX",
            "source_coverage": ["alpaca"],
            "source_observations": {
                "alpaca": {
                    "feed": "iex",
                    "bid": 100.0,
                    "ask": 100.2,
                    "midpoint": 100.1,
                    "observed_at": "2026-10-01T14:00:00Z",
                    "consolidated_quote": False,
                    "execution_grade_quote": False,
                }
            },
        },
        {
            "symbol": "MSFT",
            "source": "Alpaca IEX",
            "source_coverage": ["alpaca"],
            "source_observations": {
                "alpaca": {
                    "feed": "iex",
                    "bid": 200.0,
                    "ask": 200.4,
                    "midpoint": 200.2,
                    "observed_at": "2026-10-01T14:00:00Z",
                    "consolidated_quote": False,
                    "execution_grade_quote": False,
                }
            },
        },
    ]
    return {
        "source": "alpaca-iex-owner-development",
        "reason": "Alpaca scan",
        "symbols": rows,
        "sectors": [{"name": "Source-backed attention", "symbols": [dict(x) for x in rows]}],
        "market_health": {},
        "soulaana": {},
    }


def test_public_augments_alpaca_without_overwriting_it():
    def quote_reader(_sid, symbol, kind):
        assert kind == "EQUITY"
        values = {"AAPL": (100.1, 100.3, 100.2), "MSFT": (200.1, 200.5, 200.3)}
        bid, ask, last = values[symbol]
        return {
            "provider": "public",
            "state": "SOURCE_BOUND",
            "kind": "PUBLIC_PERSONAL_REALTIME_QUOTE",
            "symbol": symbol,
            "bid": bid,
            "ask": ask,
            "last": last,
            "observed_at": "2026-10-01T14:00:01Z",
            "owner_display_reviewed": True,
            "soulaana_ai_use_reviewed": True,
            "consolidated_quote": False,
        }

    app = SimpleNamespace(extensions={
        "ob_public_owner_quote_reader_v1": quote_reader,
    })
    doc = _merge_public_owner_context(app, base_document(), "tower_session_" + "x"*20)

    assert doc["source"] == "observatory-multi-provider-owner-research"
    assert doc["source_fusion"]["providers_present"] == ["alpaca", "public"]
    assert doc["source_fusion"]["single_provider_selected_as_truth"] is False
    assert doc["source_fusion"]["provider_values_overwritten"] is False
    assert doc["source_fusion"]["public_quote_symbols"] == 2
    assert doc["source_fusion"]["soulaana_public_quote_symbols"] == 2

    for row in doc["symbols"]:
        assert row["source_coverage"] == ["alpaca", "public"]
        assert set(row["source_observations"]) == {"alpaca", "public"}
        assert row["source_observations"]["alpaca"]["midpoint"] > 0
        assert row["source_observations"]["public"]["midpoint"] > 0
        assert row["source_comparison"]["sources_compared"] == ["alpaca", "public"]
        assert row["source_comparison"]["winner_selected"] is False
        assert row["source_comparison"]["dispersion_percent"] is not None

    assert len(doc["sectors"]) == 1
    assert len(doc["sectors"][0]["symbols"]) == 2
    assert doc["soulaana"]["source_fusion"]["single_provider_selected"] is False


def test_public_hold_does_not_remove_alpaca_or_fake_multisource():
    app = SimpleNamespace(extensions={
        "ob_public_owner_quote_reader_v1": lambda *_: {
            "provider": "public",
            "state": "RIGHTS_OR_FETCH_HOLD",
            "owner_display_reviewed": False,
            "soulaana_ai_use_reviewed": False,
        },
    })
    doc = _merge_public_owner_context(app, base_document(), "tower_session_" + "x"*20)
    assert doc["source"] == "alpaca-iex-owner-development"
    assert doc["source_fusion"]["providers_present"] == ["alpaca"]
    assert doc["source_fusion"]["public_quote_symbols"] == 0
    assert all(row["source_coverage"] == ["alpaca"] for row in doc["symbols"])
    assert all("public" not in row["source_observations"] for row in doc["symbols"])
