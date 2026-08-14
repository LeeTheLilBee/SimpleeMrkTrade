from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "web/static/ob/ob_dashboard.js").read_text(encoding="utf-8")


def test_obux017_soulaana_is_primary_intelligence():
    assert "soulaana_is_primary_intelligence: true" in JS
    assert 'class="ob-command-soulaana-story"' in JS
    assert "WHAT THIS MEANS · WHY IT MATTERS" in JS
    assert "YOUR ACCOUNT" in JS
    assert "WHAT NEEDS YOU" in JS
    assert "NEXT BEST MOVE" in JS


def test_obux017_secondary_translation_is_layered():
    assert 'class="ob-command-intelligence-strip"' in JS
    assert "WHAT I'M WATCHING" in JS
    assert "WHAT CHANGED" in JS
    assert "WHAT CAN WAIT" in JS
