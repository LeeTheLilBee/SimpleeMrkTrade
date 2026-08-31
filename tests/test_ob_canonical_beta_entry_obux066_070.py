
from pathlib import Path

from flask import Flask

from tower import (
    tower_human_login_ob_launch
    as launch_module
)


ROOT = Path(__file__).resolve().parents[1]

TOWER = ROOT / "tower/tower_human_login_ob_launch.py"
ROUTE_WALL = ROOT / "tower/ob_web_route_enforcement.py"
DASH = ROOT / "web/templates/dashboard.html"
ARRIVAL = ROOT / "web/static/ob/ob_session_arrival.js"
CLEANUP = ROOT / "web/static/ob/ob_beta_surface_cleanup.js"
THEMES = ROOT / "web/static/ob/ob_interchangeable_themes.css"


def text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def test_obux066_product_entry_remains_real_dashboard():
    assert (
        '"/ob/dashboard"'
        in text(TOWER)
    )


def test_obux066_walkthrough_is_not_product_launch_result(
    monkeypatch,
):
    app = Flask(__name__)
    app.secret_key = "obux091-product-entry-test"

    monkeypatch.setattr(
        launch_module,
        "_launch_observatory_legacy",
        lambda: launch_module.redirect(
            launch_module
            .OBSERVATORY_WALKTHROUGH_PATH
        ),
    )

    monkeypatch.setattr(
        launch_module,
        "_tower_ob_native_store_walkthrough_handoff",
        lambda: {
            "stored": True,
        },
    )

    with app.test_request_context(
        "/tower/launch/observatory"
    ):
        fn = launch_module.launch_observatory

        result = (
            fn.__wrapped__()
            if hasattr(
                fn,
                "__wrapped__",
            )
            else fn()
        )

    assert result.status_code == 302

    assert result.headers[
        "Location"
    ].endswith(
        "/ob/dashboard"
    )


def test_obux066_dashboard_remains_fail_closed_route():
    source = text(ROUTE_WALL)

    assert '"/ob/dashboard"' in source
    assert "owner_session_active()" in source
    assert "step_up_active()" in source


def test_obux067_dashboard_versions_force_new_product_build():
    source = text(DASH)

    assert (
        'data-ob-build="OBUX091-095"'
        in source
    )

    assert (
        'data-ob-whats-new-version="obux091-095-v1"'
        in source
    )


def test_obux067_arrival_system_still_available():
    source = text(ARRIVAL)

    for token in [
        "URLSearchParams",
        "openCheckIn",
        "openGuideOffer",
        "history.replaceState",
    ]:
        assert token in source


def test_obux068_theme_still_owns_product_sky():
    source = text(THEMES)

    assert "body[data-ob-room]" in source
    assert ".ob-sky" in source
    assert "--ob-theme-bg" in source


def test_obux069_new_dashboard_layout_is_intact():
    source = text(DASH)

    for token in [
        "SOULAANA · MARKET BRIEFING",
        "See the sky",
        "Study a symbol",
        "Practice",
        "MARKET GLANCE",
        "More from your Observatory",
    ]:
        assert token in source


def test_obux069_normal_dashboard_has_no_owner_intelligence_ui():
    source = text(DASH)

    for forbidden in [
        "CAPITAL LANES",
        "TODAY’S EDGE",
        "OWNER RESEARCH",
        "Enter this lane",
        "ob_mission_accounts.js",
    ]:
        assert forbidden not in source
