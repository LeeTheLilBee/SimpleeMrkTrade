from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "web/static/ob/ob_dashboard.js").read_text(encoding="utf-8")
CSS = (ROOT / "web/static/ob/ob_dashboard_soulaana_obux.css").read_text(encoding="utf-8")


def test_obux018_support_is_an_asymmetric_instrument_board():
    assert 'class="ob-command-instrument-grid"' in JS
    assert "asymmetric_instrument_board: true" in JS
    assert ".ob-command-instrument-grid" in CSS
    assert "repeat(12, minmax(0, 1fr))" in CSS


def test_obux018_instruments_are_supporting_not_primary_raw_finance():
    assert "raw_financial_metrics_primary_surface: false" in JS
    assert "RISK POSTURE" in JS
    assert "OPEN BOOK" in JS
    assert "WORTH EYES" in JS
