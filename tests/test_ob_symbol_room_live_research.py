from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_symbol_room_fuses_research_into_impact_read_and_keeps_sources_underneath():
    template = (ROOT / "web/templates/symbol_page.html").read_text()
    script = (ROOT / "web/static/ob/ob_symbol_research.js").read_text()
    css = (ROOT / "web/static/ob/ob_symbol_room.css").read_text()

    for marker in (
        'id="symbolImpactHeadline"',
        'id="symbolImpactSummary"',
        'id="symbolImpactTailwinds"',
        'id="symbolImpactHeadwinds"',
        'id="symbolImpactAgreement"',
        'id="symbolImpactConflict"',
        'id="symbolImpactWhy"',
        'id="symbolImpactWatch"',
        'Show the evidence underneath this read',
    ):
        assert marker in template

    assert "RESEARCH ROOM" not in template
    assert "SOULAANA · SYMBOL IMPACT READ" in template
    assert 'id="symbolServerResearch"' in template
    assert "/static/ob/ob_symbol_research.js?v=symbolimpact001" in template

    assert "buildImpact(" in script
    assert "sectorSensitivity(" in script
    assert "BLS + Treasury" in script
    assert "SEC EDGAR" in script
    assert "Federal Register" in script
    assert "CFTC" in script
    assert "EIA" in script
    assert "research synthesis, not a trade recommendation" in script
    assert ".ob-symbol-impact-grid" in css
    assert ".ob-symbol-evidence-drawer" in css
