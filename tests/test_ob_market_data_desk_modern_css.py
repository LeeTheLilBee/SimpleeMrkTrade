from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_market_data_desk_does_not_load_legacy_research_css():
    html = (ROOT / "web/templates/market_data_desk.html").read_text()
    assert "ob_market_data_desk.css" in html
    assert "ob_keyless_context.css" not in html


def test_market_data_desk_owns_research_component_skin():
    css = (ROOT / "web/static/ob/ob_market_data_desk.css").read_text()
    for selector in (
        'body[data-ob-room="market-data-desk"] .ob-keyless-context',
        'body[data-ob-room="market-data-desk"] .ob-keyless-card',
        'body[data-ob-room="market-data-desk"] .ob-keyless-soulaana',
        'body[data-ob-room="market-data-desk"] details.ob-keyless-evidence-drawer',
    ):
        assert selector in css
    assert "rgba(150,111,235,.12)" not in css
    assert "linear-gradient(160deg,#03050d,#090e20" not in css
