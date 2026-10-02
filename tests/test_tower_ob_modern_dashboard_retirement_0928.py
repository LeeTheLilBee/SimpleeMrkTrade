"""TWR-OBUX: the Tower-protected Observatory now renders the modern product, not old proof UI."""
from pathlib import Path

from flask import Flask, render_template

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "web/templates/dashboard.html"
STATIC = ROOT / "web/static/ob"


def test_tower_dashboard_is_the_real_source_backed_ob_product():
    text = TEMPLATE.read_text(encoding="utf-8")
    for required in (
        'data-ob-surface="user-dashboard"',
        'data-ob-dashboard-role="normal"',
        'data-ob-owner-dashboard="false"',
        'data-ob-entry="checkin-carousel-then-dashboard"',
        'id="obArrivalRoot"',
        'id="ob-app"',
        'ob_checkin_entry.js',
        'ob_dashboard_projection.js',
        'ob_dashboard_obux.css',
        'ob_product_surface_policy.js',
        'ob_session_state.js',
        'ob_global_session_shell.js',
        'Live Auto Locked',
    ):
        assert required in text, required
    for retired in (
        "ob_mission_accounts.js",
        "ob_room_data_polish.js",
        "ob_account_experience.js",
        "ob_dashboard_simplification_obux.js",
        "ob_dashboard_soulaana_obux.css",
        "ob_manual_live_checklist_record_save_flow.js",
        "Current Mission Account",
        "Room-Level Data Polish",
        "Canonical Web Protection",
    ):
        assert retired not in text, retired


def test_protected_dashboard_template_renders_without_additional_route_or_auth():
    app = Flask(__name__, template_folder=str(ROOT / "web/templates"))
    with app.test_request_context("/ob/dashboard"):
        html = render_template("dashboard.html")
    assert '<div id="obArrivalRoot"' in html
    assert "ob_checkin_entry.js" in html
    assert 'data-ob-surface="user-dashboard"' in html
    assert "ob_mission_accounts.js" not in html
    assert "ob_room_data_polish.js" not in html


def test_all_new_scripts_are_real_and_old_mission_renderers_are_not_loaded():
    text = TEMPLATE.read_text(encoding="utf-8")
    for asset in (
        "ob_interchangeable_themes.css", "ob_dashboard_obux.css",
        "ob_product_surface_policy.js", "ob_session_state.js",
        "ob_dashboard_projection.js", "ob_checkin_entry.js",
        "ob_checkin_entry.css", "ob_dashboard.js",
        "ob_global_session_shell.js", "ob_theme_switcher.js",
        "ob_beta_surface_cleanup.js",
    ):
        assert (STATIC / asset).is_file(), asset
    assert "ob_session_arrival.js" not in text
    assert "ob_dashboard_simplification_obux.js" not in text


def test_checkin_is_voluntary_but_beta_ack_is_not_bypassed():
    source = (STATIC / "ob_checkin_entry.js").read_text(encoding="utf-8")
    for phrase in (
        "acknowledgeSop(", "acknowledgeWhatsNew(",
        "skipCheckIn(", "saveCheckIn(", "acceptedSop",
        "firstSop", "Skip check-in", "ob-entry-pending",
        "ob:arrival-complete", "/tower/return/observatory",
    ):
        assert phrase in source
    assert 'if (step.kind === "beta" && firstSop && !acceptedSop)' in source
    for dangerous in ("placeOrder(", "submitOrder(", "broker.submit(", "fetch("):
        assert dangerous not in source
