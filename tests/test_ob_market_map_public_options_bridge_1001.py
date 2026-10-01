from pathlib import Path

from tower.ob_market_source_status import _canonical_public_option_contracts

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = (ROOT / "web/static/ob/ob_engine_feed_adapter.js").read_text(encoding="utf-8")
MAP_TEMPLATE = (ROOT / "web/templates/market_map.html").read_text(encoding="utf-8")
SOURCE_STATUS = (ROOT / "tower/ob_market_source_status.py").read_text(encoding="utf-8")


def test_market_map_room_scoped_feed_override_is_honored():
    assert "window.OB_ENGINE_FEED_ENDPOINT" in MAP_TEMPLATE
    assert "configuredEndpoint" in ADAPTER
    assert 'configuredEndpoint.startsWith("/ob/")' in ADAPTER
    assert '?engine_feed=1' in MAP_TEMPLATE


def test_failed_or_redirected_refresh_preserves_last_good_projection_as_stale():
    assert "function preserveLastGoodProjection(reason)" in ADAPTER
    assert "response.redirected" in ADAPTER
    assert 'contentType.includes("application/json")' in ADAPTER
    assert 'projection_status:\n        "stale"' in ADAPTER
    assert 'current_eligible:\n        false' in ADAPTER
    assert 'display_eligible:\n        true' in ADAPTER
    assert "instead of blanking the room" in ADAPTER


def test_public_option_contract_normalization_matches_existing_web_contract():
    rows = _canonical_public_option_contracts(
        {
            "expiration": "2026-10-02",
            "source_reference": "https://public.com/api/docs/resources/market-data/get-option-chain",
            "contracts": [
                {
                    "provider_symbol": "AAPL261002C00100000",
                    "right": "call",
                    "strike": 100.0,
                    "bid": 1.2,
                    "ask": 1.3,
                    "mid": 1.25,
                    "volume": 100,
                    "open_interest": 900,
                    "greeks": {
                        "delta": 0.52,
                        "implied_volatility": 0.31,
                    },
                }
            ],
        },
        "AAPL",
    )
    assert len(rows) == 1
    row = rows[0]
    assert row["symbol"] == "AAPL"
    assert row["underlying_symbol"] == "AAPL"
    assert row["contract_symbol"] == "AAPL261002C00100000"
    assert row["contractSymbol"] == "AAPL261002C00100000"
    assert row["expiration"] == "2026-10-02"
    assert row["mark"] == 1.25
    assert row["delta"] == 0.52
    assert row["implied_volatility"] == 0.31
    assert row["source"] == "public_options"
    assert row["source_backed"] is True
    assert row["research_only"] is True
    assert row["broker_execution"] is False
    assert row["automatic_execution"] is False
    assert row["automatic_contract_selection"] is False


def test_public_option_contracts_are_promoted_into_canonical_options_collection():
    assert "canonical_public_option_contracts.extend(canonical_contracts)" in SOURCE_STATUS
    assert 'document["options"] = existing_options' in SOURCE_STATUS
    assert 'document["public_option_contract_count"]' in SOURCE_STATUS
    assert '"public_options"' in SOURCE_STATUS
