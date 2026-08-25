
from pathlib import Path

from flask import Flask

from tower import (
    tower_human_login_ob_launch
    as launch_module
)


ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


TOWER = (
    ROOT
    / "tower"
    / "tower_human_login_ob_launch.py"
)

ROUTE_WALL = (
    ROOT
    / "tower"
    / "ob_web_route_enforcement.py"
)

DASH = (
    ROOT
    / "web"
    / "templates"
    / "dashboard.html"
)

ARRIVAL = (
    ROOT
    / "web"
    / "static"
    / "ob"
    / "ob_session_arrival.js"
)

CLEANUP = (
    ROOT
    / "web"
    / "static"
    / "ob"
    / "ob_beta_surface_cleanup.js"
)

THEMES = (
    ROOT
    / "web"
    / "static"
    / "ob"
    / "ob_interchangeable_themes.css"
)


def text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def test_obux066_product_entry_constant_is_real_dashboard():
    source = text(TOWER)

    assert (
        'OBSERVATORY_PRODUCT_ENTRY_PATH = ('
        in source
    )

    assert (
        '"/ob/dashboard"'
        in source
    )


def test_obux066_walkthrough_route_is_preserved_but_not_public_launch_result(
    monkeypatch,
):
    app = Flask(__name__)
    app.secret_key = "obux066-product-entry-test"

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
        launch_function = (
            launch_module
            .launch_observatory
        )

        result = (
            launch_function.__wrapped__()
            if hasattr(
                launch_function,
                "__wrapped__",
            )
            else launch_function()
        )

    assert result.status_code == 302

    assert result.headers[
        "Location"
    ].endswith(
        "/ob/dashboard"
    )

    assert (
        launch_module
        .OBSERVATORY_WALKTHROUGH_PATH
        == "/tower/observatory-walkthrough"
    )


def test_obux066_dashboard_is_already_inside_fail_closed_route_wall():
    source = text(ROUTE_WALL)

    assert (
        '"/ob/dashboard"'
        in source
    )

    assert (
        "owner_session_active()"
        in source
    )

    assert (
        "step_up_active()"
        in source
    )


def test_obux067_dashboard_versions_force_one_new_real_arrival():
    source = text(DASH)

    assert (
        'data-ob-build="OBUX066-070"'
        in source
    )

    assert (
        'data-ob-sop-version="beta-sop-v2"'
        in source
    )

    assert (
        'data-ob-whats-new-version="obux066-070-v1"'
        in source
    )


def test_obux067_fresh_arrival_replays_sop_checkin_and_guide():
    source = text(ARRIVAL)

    for token in [
        "URLSearchParams",
        '"ob_arrival"',
        '"fresh"',
        "forceFreshArrival",
        "openCheckIn",
        "openGuideOffer",
        "history.replaceState",
    ]:
        assert token in source

    assert (
        """await openSop(
          true,
          false
        );"""
        in source
    )

    assert (
        """await openCheckIn(
        forceFreshArrival
      );"""
        in source
    )

    assert (
        """await openGuideOffer(
        forceFreshArrival
      );"""
        in source
    )


def test_obux067_drawer_has_fresh_arrival_replay():
    source = text(CLEANUP)

    assert (
        '/ob/dashboard?ob_arrival=fresh'
        in source
    )

    assert (
        "Replay welcome & Soulaana check-in"
        in source
    )


def test_obux068_theme_owns_actual_atmosphere_layers():
    source = text(THEMES)

    assert (
        "OBUX068_THEME_OWNS_PRODUCT_SKY"
        in source
    )

    for token in [
        "body[data-ob-room]",
        ".ob-sky",
        ".ob-sky__weather",
        ".ob-sky__horizon",
        ".ob-sky__grid",
        "--ob-theme-bg",
        "--ob-theme-accent",
        "--ob-theme-gold",
    ]:
        assert token in source


def test_obux068_theme_sky_does_not_add_old_bright_blue_values():
    source = text(THEMES).lower()

    for forbidden in [
        "rgba(87, 122, 255",
        "rgba(55, 126, 255",
        "rgba(52, 131, 255",
        "#7ffcff",
        "#8fc4ff",
    ]:
        assert forbidden not in source


def test_obux069_dashboard_layout_remains_intact():
    source = text(DASH)

    for token in [
        "Account snapshot",
        "SOULAANA · RIGHT NOW",
        "SINCE YOU WERE HERE",
        "YOUR ACTIVITY",
        "MARKET NOW",
        "YOUR OPERATING LOOP",
        "MY OB",
    ]:
        assert token in source


def test_obux069_normal_dashboard_still_has_no_mission_account_ui():
    source = text(DASH).lower()

    assert (
        "ob_mission_accounts.js"
        not in source
    )

    assert (
        "mission_accounts"
        not in source
    )


def test_obux069_no_execution_capability_added():
    source = (
        text(ARRIVAL)
        + "\n"
        + text(CLEANUP)
        + "\n"
        + text(THEMES)
    )

    for forbidden in [
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "automaticContractSelection = true",
    ]:
        assert forbidden not in source
