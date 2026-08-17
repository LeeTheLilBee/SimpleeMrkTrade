from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = (
    ROOT / "web/templates/owner_dashboard.html"
).read_text(encoding="utf-8")

CSS = (
    ROOT / "web/static/ob/ob_owner_dashboard.css"
).read_text(encoding="utf-8")

APP = (
    ROOT / "web/app.py"
).read_text(encoding="utf-8")


def test_obux025_history_is_preserved_after_activation_handoff():
    # OBUX025 records the historical dormant design stage.
    assert "OBUX025_DORMANT_OWNER_DASHBOARD" in TEMPLATE

    # The later activation handoff is now the current state.
    assert "OWNER_DASHBOARD_ACTIVATION_HANDOFF" in TEMPLATE
    assert 'data-ob-owner-dashboard-role="owner-only-active"' in TEMPLATE
    assert 'data-ob-owner-dashboard-route-state="tower-protected-active"' in TEMPLATE
    assert 'data-ob-owner-dashboard-design-activated="true"' in TEMPLATE
    assert "Tower Protected" in TEMPLATE

    # Only the canonical protected OB route remains.
    assert '@app.route("/ob/owner-dashboard")' in APP
    assert '@app.route("/owner-dashboard")' not in APP

    assert (
        'def ob_owner_dashboard_v17():\n'
        '    return render_template("owner_dashboard.html")'
    ) in APP


def test_obux025_owner_dashboard_does_not_load_owner_console_stack():
    assert "ob_owner_console.js" not in TEMPLATE
    assert "ob_owner_source_audit.js" not in TEMPLATE
    assert "ob_private_beta_launch_control.js" not in TEMPLATE
    assert "ob_manual_live_operator_confidence_readiness_checkpoint.js" not in TEMPLATE


def test_obux025_visual_identity_is_high_altitude_observatory():
    assert ".ob-owner-hero" in CSS
    assert ".ob-owner-observatory" in CSS
    assert ".ob-owner-briefing-river" in CSS
    assert ".ob-owner-instrument-grid" in CSS
    assert ".ob-owner-lower-grid" in CSS
    assert "radial-gradient" in CSS


def test_obux025_live_auto_lock_remains_visible_after_activation():
    assert "Live Auto Locked" in TEMPLATE
    assert "owner-only-active" in TEMPLATE
