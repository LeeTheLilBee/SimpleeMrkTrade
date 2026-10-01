from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_symbol_soulaana_exposes_actual_provider_ai_use_and_translates_findings():
    backend = (ROOT / "tower/ob_keyed_provider_research.py").read_text()
    script = (ROOT / "web/static/ob/ob_symbol_research.js").read_text()

    assert '"owner_display_reviewed"' in backend
    assert '"soulaana_ai_use_reviewed"' in backend
    assert "[OB_PROVIDER_RESEARCH_STATE]" in backend

    assert "visible + actually readable by Soulaana" in script
    assert "Soulaana AI-use review is OFF" in script
    assert "providerObservations" in script
    assert "x && x.finding" in script
    assert "x && x.why_it_matters" in script
    assert "what_is_missing" in script
