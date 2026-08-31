from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = (
    ROOT / "web/templates/owner_dashboard.html"
).read_text(
    encoding="utf-8",
    errors="replace",
)

CSS = (
    ROOT / "web/static/ob/ob_owner_dashboard.css"
).read_text(
    encoding="utf-8",
    errors="replace",
)

APP = (
    ROOT / "web/app.py"
).read_text(
    encoding="utf-8",
    errors="replace",
)


def test_obux025_history_is_preserved_after_clean_slate_activation():
    assert (
        "OBUX025_DORMANT_OWNER_DASHBOARD"
        in TEMPLATE
    )

    assert (
        "OWNER_DASHBOARD_ACTIVATION_HANDOFF"
        in TEMPLATE
    )

    for marker in [
        'data-ob-owner-dashboard-role="owner-only-active"',
        'data-ob-owner-dashboard-route-state="tower-protected-active"',
        'data-ob-owner-dashboard-design-activated="true"',
        'data-ob-owner-capital-lanes="true"',
        'data-ob-owner-intelligence-cockpit="true"',
        'data-ob-build="OBUX091-095"',
    ]:
        assert marker in TEMPLATE

    assert "Tower Protected" in TEMPLATE

    assert '@app.route("/ob/owner-dashboard")' in APP
    assert '@app.route("/owner-dashboard")' not in APP


def test_obux025_owner_dashboard_does_not_load_owner_console_stack():
    for forbidden in [
        "ob_owner_console.js",
        "ob_owner_source_audit.js",
        "ob_private_beta_launch_control.js",
        "ob_manual_live_operator_confidence_readiness_checkpoint.js",
    ]:
        assert forbidden not in TEMPLATE


def test_obux025_visual_identity_is_attention_first_owner_cockpit():
    for marker in [
        ".ob-owner-hero",
        ".ob-owner-edge-grid",
        ".ob-owner-context-grid",
        ".ob-owner-attention-section",
        ".ob-owner-more",
        ".ob-capital-lanes-section",
        ".ob-owner-drawer",
        "radial-gradient",
    ]:
        assert marker in CSS


def test_obux025_accessibility_survives_clean_slate():
    assert "focus-visible" in CSS
    assert "prefers-reduced-motion" in CSS


def test_obux025_live_auto_lock_remains_visible():
    assert "Live Auto Locked" in TEMPLATE
    assert "owner-only-active" in TEMPLATE
