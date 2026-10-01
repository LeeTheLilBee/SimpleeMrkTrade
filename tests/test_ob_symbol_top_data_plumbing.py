from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_symbol_top_cards_are_hydrated_from_provider_research_and_cache_is_busted():
    template = (ROOT / "web/templates/symbol_page.html").read_text()
    script = (ROOT / "web/static/ob/ob_symbol_research.js").read_text()
    provider = (ROOT / "tower/ob_keyed_provider_research.py").read_text()

    assert "/static/ob/ob_symbol_research.js?v=symboltop002" in template
    assert "hydrateTopSymbolFacts(" in script
    assert 'byId("symbolUnderlyingMetrics")' in script
    assert 'byId("symbolStarFacts")' in script
    assert 'set("symbolCompany"' in script
    assert 'set("symbolSector"' in script
    assert 'set("symbolMarketState"' in script
    assert "Current midpoint" in script
    assert "Last daily close" in script
    assert "Market cap" in script
    assert "Shares outstanding" in script

    for field in (
        '"country"', '"currency"', '"website"',
        '"market_cap_millions"', '"shares_outstanding_millions"',
    ):
        assert field in provider
