from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_front_page_stays_ultra_calm():
    html = (ROOT / "web/templates/dashboard.html").read_text()
    assert "ob-user-focus-compact" in html
    assert "Right now." in html
    assert "ob-data-pulse" in html
    assert "ob-user-paths" not in html
    assert "More from your Observatory" not in html
    assert "ob-user-boundary-note" not in html
    assert "See the market." not in html


def test_dashboard_does_not_auto_launch_guide():
    js = (ROOT / "web/static/ob/ob_dashboard.js").read_text()
    assert "showDashboardGuide" in js
    assert "window.setTimeout(\n      showDashboardGuide" not in js
    assert "renderMore(\n      projection.more" not in js


def test_dashboard_glance_cards_are_scan_first():
    css = (ROOT / "web/static/ob/ob_dashboard_obux.css").read_text()
    assert ".ob-user-focus-compact" in css
    assert ".ob-user-glance-card p{display:none}" in css
    assert ".ob-guide-prompt{display:none!important}" in css
