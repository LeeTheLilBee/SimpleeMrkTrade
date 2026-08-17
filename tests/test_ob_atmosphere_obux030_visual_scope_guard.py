from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CSS = (
    ROOT
    / "web/static/ob/ob_atmosphere.css"
).read_text(
    encoding="utf-8"
)

APP = (
    ROOT
    / "web/app.py"
).read_text(
    encoding="utf-8"
)


def test_obux030_is_visual_only():
    assert "visual_only: true" in CSS
    assert "route_changes: false" in CSS
    assert "permission_changes: false" in CSS
    assert "broker_execution: false" in CSS
    assert "capital_action: false" in CSS
    assert "live_auto_locked: true" in CSS
    assert "gp066_advanced: false" in CSS


def test_obux030_owner_dashboard_route_is_still_not_created_here():
    assert "/ob/owner-dashboard" not in APP


def test_obux030_atmosphere_contains_no_behavioral_javascript():
    assert "fetch(" not in CSS
    assert "XMLHttpRequest" not in CSS
    assert "WebSocket" not in CSS
