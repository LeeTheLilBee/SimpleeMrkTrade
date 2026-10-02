from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_symbol_source_accounting_covers_every_active_research_lane():
    template = (ROOT / "web/templates/symbol_page.html").read_text()
    script = (ROOT / "web/static/ob/ob_symbol_research.js").read_text()

    assert 'id="symbolSourceAccounting"' in template
    assert 'id="symbolServerResearch"' in template
    assert "/static/ob/ob_symbol_research.js?v=publicoptions005" in template

    for source in (
        "finnhub","alpha_vantage","finazon","alpaca","public","public_options","bea",
        "bls","treasury","openfigi",
        "federal_register","cftc","eia","world_bank","nws",
        "sec_edgar",
    ):
        assert source in script

    assert "renderSourceAccounting(" in script
    assert "visible + actually readable by Soulaana" in script
    assert "visible to owner, but Soulaana AI-use review is OFF" in script
    assert "Soulaana accounts for the mapping" in script
    assert "applies it only when it is relevant enough to this symbol" in script
    assert "server-side issuer packet not attached" in script
