from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "web/static/ob/ob_dashboard.js").read_text(encoding="utf-8")
CSS = (ROOT / "web/static/ob/ob_dashboard_soulaana_obux.css").read_text(encoding="utf-8")


def test_obux016_command_stage_replaces_equal_card_hero():
    assert 'class="ob-command-stage"' in JS
    assert 'class="ob-command-stage-main"' in JS
    assert 'class="ob-command-sky-instrument"' in JS
    assert 'class="ob-command-orbit"' in JS
    assert "SOULAANA · RIGHT NOW" in JS
    assert "MARKET READ" in JS


def test_obux016_observatory_visual_identity_exists():
    assert ".ob-command-stage" in CSS
    assert ".ob-command-orbit-ring" in CSS
    assert ".ob-command-orbit-core" in CSS
    assert ".ob-command-star" in CSS
    assert "radial-gradient" in CSS
