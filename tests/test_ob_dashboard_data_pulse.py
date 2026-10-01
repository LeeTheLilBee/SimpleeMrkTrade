from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_uses_compact_data_pulse_not_full_research_wall():
    html = (ROOT / "web/templates/dashboard.html").read_text()
    assert 'id="obDataPulseChips"' in html
    assert 'href="/ob/data-desk"' in html
    assert "ob_dashboard_data_pulse.js" in html
    assert "ob_keyless_context.css" not in html
    assert 'id="obKeylessContextRoot"' not in html
    assert "ob_keyless_context.js" not in html
    assert "ob_official_catalyst_radar.js" not in html


def test_dashboard_pulse_is_bounded_reviewed_context():
    js = (ROOT / "web/static/ob/ob_dashboard_data_pulse.js").read_text()
    assert '"/ob/research/keyless.json"' in js
    assert '"/ob/research/catalysts.json"' in js
    assert '"/ob/engine-feed-snapshot.json"' in js
    assert "observation_count" in js
    assert "observations.slice(0,3)" in js
    assert "factual_findings[0]" in js
    assert "how_to_interpret" in js
    assert "source_reference" not in js
    assert "innerHTML" not in js


def test_dashboard_pulse_uses_current_dashboard_css():
    css = (ROOT / "web/static/ob/ob_dashboard_obux.css").read_text()
    assert ".ob-data-pulse" in css
    assert ".ob-data-chip" in css
    assert "Settings → Market Data Desk" in css
