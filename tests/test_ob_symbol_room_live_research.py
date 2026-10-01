from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_symbol_room_integrates_provider_research_and_hides_generic_bottom_dump():
    template = (ROOT / "web/templates/symbol_page.html").read_text()
    script = (ROOT / "web/static/ob/ob_symbol_research.js").read_text()
    css = (ROOT / "web/static/ob/ob_symbol_room.css").read_text()

    assert 'id="symbolResearchStatus"' in template
    assert 'id="symbolResearchSoulaana"' in template
    assert "/static/ob/ob_symbol_research.js?v=symbolresearch001" in template
    assert 'id="obKeylessContextRoot"' in template
    assert "ob-symbol-hidden-shared-research" in template
    assert ".ob-symbol-hidden-shared-research{display:none!important;}" in css

    assert 'fetch("/ob/research/providers.json?symbol="' in script
    assert "Alpaca IEX" in script
    assert "finnhub" in script
    assert "alpha_vantage" in script
    assert "bea" in script
    assert "No data was invented" in script
