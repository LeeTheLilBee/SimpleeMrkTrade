from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_front_page_stays_birdseye_not_research_wall():
    html = (ROOT / "web/templates/dashboard.html").read_text()
    assert "ob-command-dashboard" in html
    assert "SOULAANA · RIGHT NOW" in html
    assert "ACCOUNT HEALTH" in html
    assert "MARKET GLANCE" in html
    assert "RISK / DANGER" in html
    assert "WHAT CHANGED" in html
    assert "WATCH / ATTENTION" in html
    assert "ACTIVE TRADES" in html
    assert "UPCOMING CATALYSTS" in html
    assert "ob-data-pulse-chips" in html
    assert "ob-user-paths" not in html
    assert "More from your Observatory" not in html


def test_dashboard_has_no_auto_launch_guide():
    js = (ROOT / "web/static/ob/ob_dashboard.js").read_text()
    assert "showDashboardGuide" not in js
    assert "setTimeout" not in js
    assert "renderMore(" not in js
    assert 'document.addEventListener("DOMContentLoaded", boot' in js


def test_dashboard_glance_cards_are_scan_first():
    css = (ROOT / "web/static/ob/ob_dashboard_obux.css").read_text()
    assert ".ob-user-focus-compact" in css
    assert ".ob-user-glance-card p{display:none}" in css
    assert ".ob-guide-prompt{display:none!important}" in css
