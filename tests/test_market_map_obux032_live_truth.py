from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

JS = (
    ROOT / "web/static/ob/ob_market_map.js"
).read_text(encoding="utf-8")

ADAPTER = (
    ROOT / "web/static/ob/ob_engine_feed_adapter.js"
).read_text(encoding="utf-8")

CONTRACTS = (
    ROOT / "web/static/ob/ob_data_contracts.js"
).read_text(encoding="utf-8")


def test_obux032_existing_adapter_is_60_second_canonical_feed():
    assert '"/ob/engine-feed-snapshot.json"' in ADAPTER
    assert "60 * 1000" in ADAPTER
    assert "obEngineFeedAdapterUpdated" in ADAPTER


def test_obux032_market_map_uses_canonical_contract_and_projection():
    assert "OB_DATA_CONTRACTS_V22" in JS
    assert "marketMapContract" in JS

    assert "OB_ENGINE_FEED_ADAPTER_V25" in JS
    assert "getProjection" in JS


def test_obux032_feed_event_rerenders_market_map():
    assert (
        'window.addEventListener(\n'
        '      "obEngineFeedAdapterUpdated"'
        in JS
    )

    assert "handleCanonicalFeedUpdate" in JS
    assert 'render(\n      "obEngineFeedAdapterUpdated"' in JS


def test_obux032_event_handler_rereads_truth_instead_of_trusting_event_payload():
    assert (
        "do not trust a copied event payload as room truth"
        in JS
    )

    assert "marketMapContract()" in JS
    assert "canonicalProjection()" in JS


def test_obux032_market_map_has_no_independent_market_transport():
    assert "fetch(" not in JS
    assert "XMLHttpRequest" not in JS
    assert "new WebSocket" not in JS
    assert "new EventSource" not in JS


def test_obux032_market_map_does_not_consume_demo_fixture():
    assert "OB_MARKET_DATA" not in JS
    assert "Fallback Sector" not in JS


def test_obux032_contract_is_existing_canonical_market_map_contract():
    assert "function marketMapContract()" in CONTRACTS
    assert "open_positions" in CONTRACTS
    assert "candidates" in CONTRACTS
    assert "freshness" in CONTRACTS
    assert "as_of" in CONTRACTS


def test_obux032_ui_age_timer_is_not_data_polling():
    assert "refreshRelativeAgeOnly" in JS
    assert "UI clock only." in JS
    assert "This does NOT fetch data" in JS
