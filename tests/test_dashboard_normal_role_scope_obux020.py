from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "web/static/ob/ob_dashboard.js").read_text(encoding="utf-8")
HTML = (ROOT / "web/templates/dashboard.html").read_text(encoding="utf-8")


def test_obux020_dashboard_is_explicitly_normal_dashboard():
    assert 'data-ob-dashboard-role="normal"' in HTML
    assert "NORMAL_OB_DASHBOARD_ONLY" in HTML
    assert 'data-dashboard-role="normal"' in JS
    assert 'dashboard_role: (' in JS
    assert '"normal"' in JS
    assert "normal_dashboard_only: true" in JS


def test_obux020_owner_surfaces_remain_separate():
    assert "owner_dashboard_surface: false" in JS
    assert "owner_console_surface: false" in JS
    assert "owner_admin_controls_primary: false" in JS


def test_obux020_live_execution_remains_locked():
    assert "live_auto_locked: true" in JS
    assert "broker_action_performed: false" in JS
    assert "capital_action_performed: false" in JS
    assert "permission_mutation_performed: false" in JS
