from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_market_data_desk_is_explanation_first():
    html = (ROOT / "web/templates/market_data_desk.html").read_text()
    assert "What OB can see, what it means, and what needs attention." in html
    assert "<summary>How this desk works</summary>" in html
    assert "<summary>Evidence rules</summary>" in html
    assert "<summary>Show connection evidence</summary>" in html
    assert "From discovery to trusted observation" not in html


def test_keyless_research_hides_source_cards_by_default():
    js = (ROOT / "web/static/ob/ob_keyless_context.js").read_text()
    assert 'el("details", "ob-keyless-evidence-drawer")' in js
    assert '"Show source evidence"' in js
    assert '"SOULAANA · PLAIN ENGLISH"' in js
    assert '"SOULAANA · WHAT IT MEANS"' in js


def test_catalyst_radar_explains_before_source_records():
    js = (ROOT / "web/static/ob/ob_official_catalyst_radar.js").read_text()
    assert '"SOULAANA · CATALYST READ"' in js
    assert '"What matters"' in js
    assert '"Show source records"' in js
    assert '"Show provenance & timeline"' in js


def test_explanation_first_drawers_use_current_ob_styles():
    css = (ROOT / "web/static/ob/ob_keyless_context.css").read_text()
    desk_css = (ROOT / "web/static/ob/ob_market_data_desk.css").read_text()
    assert ".ob-keyless-takeaways" in css
    assert ".ob-keyless-evidence-drawer" in css
    assert ".mdd-background-drawer" in desk_css
    assert ".mdd-evidence-drawer" in desk_css
