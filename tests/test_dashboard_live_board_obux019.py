from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "web/static/ob/ob_dashboard.js").read_text(encoding="utf-8")
CSS = (ROOT / "web/static/ob/ob_dashboard_soulaana_obux.css").read_text(encoding="utf-8")


def test_obux019_open_book_and_hot_now_share_live_board():
    assert 'class="ob-command-live-board"' in JS
    assert 'class="ob-command-live-column open-book-column"' in JS
    assert 'class="ob-command-live-column hot-now-column"' in JS
    assert "compact_live_board: true" in JS
    assert ".ob-command-live-board" in CSS


def test_obux019_source_truth_guards_remain():
    assert "static_market_fallback_actionable: false" in JS
    assert "static_market_fallback_confirmed_position: false" in JS
    assert '["MU", "AMD", "INTC"].includes' not in JS
    assert "sample_signals" not in JS
