from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_is_birdseye_command_center():
    html = (ROOT / "web/templates/dashboard.html").read_text()
    for expected in (
        "SOULAANA · RIGHT NOW",
        "ACCOUNT HEALTH",
        "MARKET GLANCE",
        "RISK / DANGER",
        "WHAT CHANGED",
        "WATCH / ATTENTION",
        "ACTIVE TRADES",
        "UPCOMING CATALYSTS",
        "DATA HEALTH",
        "SOULAANA · NEXT",
    ):
        assert expected in html
    assert "obKeylessContextRoot" not in html
    assert "Open sanitized connection status" not in html
    assert "API Key Desk" not in html


def test_dashboard_projection_uses_existing_truth_without_inventing_account_values():
    js = (ROOT / "web/static/ob/ob_dashboard_projection.js").read_text()
    assert "projection.account_snapshot" in js
    assert "projection.positions_preview" in js
    assert "projection.warnings" in js
    assert "projection.manual_live_queue" in js
    assert '"Account truth unavailable"' in js
    assert '"No verified account snapshot is attached."' in js
    assert "owner_capital_lanes:\n        false" in js
    assert "automatic_execution:\n        false" in js


def test_dashboard_research_is_summary_only():
    js = (ROOT / "web/static/ob/ob_dashboard_data_pulse.js").read_text()
    assert '"/ob/research/keyless.json"' in js
    assert '"/ob/research/catalysts.json"' in js
    assert "factual_findings" in js
    assert "event_timeline" in js
    assert "source_reference" not in js
    assert "Original record" not in js
    assert "provider_payload" not in js


def test_dashboard_renderer_has_no_account_identifier_surface():
    js = (ROOT / "web/static/ob/ob_dashboard.js").read_text()
    assert "obAccountHealthFacts" in js
    assert "obPositionsList" in js
    assert "account_id" not in js
    assert "access_token" not in js
    assert "api_key" not in js
