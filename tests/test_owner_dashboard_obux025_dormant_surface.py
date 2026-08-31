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


def test_obux025_history_is_preserved_after_capital_lane_activation():
    # Historical dormant stage remains documented.
    assert (
        "OBUX025_DORMANT_OWNER_DASHBOARD"
        in TEMPLATE
    )

    # Current owner-only activation remains authoritative.
    assert (
        "OWNER_DASHBOARD_ACTIVATION_HANDOFF"
        in TEMPLATE
    )

    assert (
        'data-ob-owner-dashboard-role="owner-only-active"'
        in TEMPLATE
    )

    assert (
        'data-ob-owner-dashboard-route-state="tower-protected-active"'
        in TEMPLATE
    )

    assert (
        'data-ob-owner-dashboard-design-activated="true"'
        in TEMPLATE
    )

    assert (
        'data-ob-owner-capital-lanes="true"'
        in TEMPLATE
    )

    assert "Tower Protected" in TEMPLATE

    # Only canonical protected OB route remains.
    assert '@app.route("/ob/owner-dashboard")' in APP

    assert '@app.route("/owner-dashboard")' not in APP

    assert (
        'def ob_owner_dashboard_v17():\n'
        '    return render_template("owner_dashboard.html")'
    ) in APP


def test_obux025_owner_dashboard_does_not_load_owner_console_stack():
    for forbidden in [
        "ob_owner_console.js",
        "ob_owner_source_audit.js",
        "ob_private_beta_launch_control.js",
        "ob_manual_live_operator_confidence_readiness_checkpoint.js",
    ]:
        assert forbidden not in TEMPLATE


def test_obux025_visual_identity_is_now_focused_capital_lanes():
    for marker in [
        ".ob-owner-hero",
        ".ob-capital-lanes-section",
        ".ob-capital-focus",
        ".ob-capital-lane-nodes",
        ".ob-owner-attention-section",
        ".ob-owner-more",
        ".ob-capital-drawer",
        "radial-gradient",
    ]:
        assert marker in CSS


def test_obux025_accessibility_is_preserved_in_focused_owner_surface():
    assert (
        "focus-visible"
        in CSS
    )

    assert (
        "prefers-reduced-motion"
        in CSS
    )


def test_obux025_live_auto_lock_remains_visible_after_activation():
    assert "Live Auto Locked" in TEMPLATE

    assert "owner-only-active" in TEMPLATE
