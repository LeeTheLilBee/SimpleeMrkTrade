from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

APP = ROOT / "web/app.py"
DASH = ROOT / "web/templates/dashboard.html"
OWNER = ROOT / "web/templates/owner_dashboard.html"


def text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def test_obfix001_dashboard_route_uses_current_template():
    app = text(APP)

    assert '@app.route("/ob/dashboard")' in app
    assert "def ob_dashboard_v16():" in app
    assert 'return render_template("dashboard.html")' in app


def test_obfix002_legacy_obux006_server_response_hijack_is_retired():
    app = text(APP)

    for forbidden in [
        "TOWER_DASHBOARD_OBUX006_010_SERVER_RENDER_WIRING_REPAIR",
        "_tower_obux006_010_dashboard_server_html",
        "_tower_obux006_010_dashboard_server_render_response",
        'id="ob-dashboard-obux006-010"',
        "x-ob-dashboard-obux006-010",
    ]:
        assert forbidden not in app


def test_obfix003_current_dashboard_is_obux091_095():
    dash = text(DASH)

    assert 'data-ob-build="OBUX091-095"' in dash
    assert "SOULAANA · MARKET BRIEFING" in dash
    assert "MARKET GLANCE" in dash
    assert "Three things max." in dash


def test_obfix003_normal_dashboard_has_no_legacy_mission_or_v27_renderer():
    dash = text(DASH)

    for forbidden in [
        "ob_mission_accounts.js",
        "ob_account_experience.js",
        "ob_room_data_polish.js",
        "/ob/account-experience.json",
        'data-ob-v27-room-data-polish="true"',
        "Room-Level Data Polish · V27",
    ]:
        assert forbidden not in dash


def test_obfix004_owner_dashboard_remains_separate_and_current():
    app = text(APP)
    owner = text(OWNER)

    assert '@app.route("/ob/owner-dashboard")' in app
    assert "def ob_owner_dashboard_v17():" in app
    assert 'return render_template("owner_dashboard.html")' in app

    assert 'data-ob-build="OBUX091-095"' in owner
    assert 'data-ob-owner-dashboard-role="owner-only-active"' in owner
    assert 'data-ob-owner-intelligence-cockpit="true"' in owner


def test_obfix005_repair_does_not_add_execution_authority():
    combined = "\n".join([
        text(APP),
        text(DASH),
        text(OWNER),
    ])

    # OBFIX only retires a presentation-response override.
    repair = text(APP).split(
        "# OBFIX001–005 — LEGACY DASHBOARD RESPONSE OVERRIDE RETIRED",
        1,
    )[1][:1800]

    for forbidden in [
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "broker.submit(",
    ]:
        assert forbidden not in repair
