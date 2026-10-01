from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_symbol_room_uses_native_full_research_without_generic_shared_shell():
    template = (ROOT / "web/templates/symbol_page.html").read_text()
    script = (ROOT / "web/static/ob/ob_symbol_research.js").read_text()

    assert 'id="symbolResearchStatus"' in template
    assert 'id="symbolResearchSoulaana"' in template
    assert 'id="symbolResearchBls"' in template
    assert 'id="symbolResearchTreasury"' in template
    assert 'id="symbolResearchFigi"' in template
    assert 'id="symbolResearchCatalysts"' in template
    assert "SEC · WHAT THE FILINGS SAY" in template
    assert "/static/ob/ob_symbol_research.js?v=symbolresearch001" in template

    assert 'id="obKeylessContextRoot"' not in template
    assert "ob_research_context_partial.html" not in template
    assert "/static/ob/ob_keyless_context.js" not in template
    assert "/static/ob/ob_official_catalyst_radar.js" not in template

    assert 'json("/ob/research/providers.json?symbol="' in script
    assert 'json("/ob/research/keyless.json?symbol="' in script
    assert 'json("/ob/research/catalysts.json")' in script
    for provider in (
        "alpaca", "finnhub", "alpha_vantage", "finazon", "bea",
        "bls", "treasury", "openfigi",
        "federal_register", "cftc", "eia", "world_bank", "nws",
    ):
        assert provider in script
    assert "JSON.stringify(rates" not in script
