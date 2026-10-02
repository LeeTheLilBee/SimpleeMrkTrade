from types import SimpleNamespace

from tower.ob_market_source_status import (
    _merge_cached_provider_context,
    _merge_public_owner_context,
)


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


class FakeProviderCache:
    def snapshot_for_symbol(self, sid, symbol):
        assert sid.startswith("tower_session_")
        if symbol != "AAPL":
            return []
        return [
            {
                "provider": "finnhub",
                "state": "SOURCE_BOUND",
                "kind": "COMPANY_REFERENCE",
                "symbol": "AAPL",
                "security_name": "Apple Inc.",
                "exchange": "NASDAQ",
                "industry": "Technology",
                "source_reference": "finnhub-ref",
                "owner_display_reviewed": True,
                "soulaana_ai_use_reviewed": True,
                "historical_only": False,
                "live_quote": False,
            },
            {
                "provider": "alpha_vantage",
                "state": "SOURCE_BOUND",
                "kind": "COMPANY_OVERVIEW_AND_COMPLETED_DAILY_HISTORY",
                "symbol": "AAPL",
                "company_profile": {
                    "name": "Apple Inc.",
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                    "market_cap": 3200000000000.0,
                },
                "bars": [
                    {"session_date": "2026-09-30", "close": 231.2},
                    {"session_date": "2026-09-29", "close": 229.8},
                ],
                "source_reference": "alpha-ref",
                "owner_display_reviewed": True,
                "soulaana_ai_use_reviewed": True,
                "historical_only": False,
                "live_quote": False,
            },
            {
                "provider": "bea",
                "state": "SOURCE_BOUND",
                "kind": "OFFICIAL_US_QUARTERLY_MACRO_CONTEXT",
                "symbol": "AAPL",
                "macro_series": [{"series_id": "real_gdp_growth", "observations": []}],
                "source_reference": "bea-ref",
                "owner_display_reviewed": True,
                "soulaana_ai_use_reviewed": True,
                "historical_only": True,
                "live_quote": False,
            },
        ]


def test_cached_provider_research_is_amalgamated_into_same_canonical_symbol_without_fetch():
    app = SimpleNamespace(extensions={"ob_provider_research_cache_v1": FakeProviderCache()})
    doc = _merge_cached_provider_context(
        app, base_document(), "tower_session_" + "x"*20)

    aapl = next(row for row in doc["symbols"] if row["symbol"] == "AAPL")
    assert set(aapl["source_coverage"]) == {"alpaca", "finnhub", "alpha_vantage"}
    assert set(aapl["source_observations"]) == {"alpaca", "finnhub", "alpha_vantage"}
    assert aapl["source_observations"]["finnhub"]["summary"]["industry"] == "Technology"
    assert aapl["source_observations"]["alpha_vantage"]["summary"]["latest_sessions"][0]["close"] == 231.2
    assert aapl["amalgamated_cached_providers"] == ["alpha_vantage", "finnhub"]

    msft = next(row for row in doc["symbols"] if row["symbol"] == "MSFT")
    assert msft["source_coverage"] == ["alpaca"]
    assert doc["shared_research_context"]["bea"]["research_only"] is True
    assert set(doc["source_fusion"]["providers_present"]) == {
        "alpaca", "alpha_vantage", "bea", "finnhub"
    }
    assert doc["source_fusion"]["single_provider_selected_as_truth"] is False
    assert doc["source_fusion"]["cached_provider_amalgamation"]["network_fetches_triggered"] is False
    assert doc["market_health"]["cached_provider_amalgamation"]["network_fetches_triggered"] is False
    assert doc["soulaana"]["source_fusion"]["cached_ai_reviewed_providers"] == [
        "alpha_vantage", "bea", "finnhub"
    ]
