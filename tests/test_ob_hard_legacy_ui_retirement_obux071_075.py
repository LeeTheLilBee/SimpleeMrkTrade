
from pathlib import Path


ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


DASH = (
    ROOT
    / "web/templates/dashboard.html"
)

POLICY = (
    ROOT
    / "web/static/ob/ob_product_surface_policy.js"
)

MISSIONS = (
    ROOT
    / "web/static/ob/ob_mission_accounts.js"
)

V27 = (
    ROOT
    / "web/static/ob/ob_room_data_polish.js"
)

THEMES = (
    ROOT
    / "web/static/ob/ob_interchangeable_themes.css"
)


def text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def test_dashboard_is_current_obux071_075_surface():
    source = text(DASH)

    assert (
        'data-ob-build="OBUX086-090"'
        in source
    )


def test_normal_dashboard_does_not_load_mission_script():
    source = text(DASH)

    assert (
        "ob_mission_accounts.js"
        not in source
    )


def test_normal_dashboard_does_not_load_v27_renderer():
    source = text(DASH)

    assert (
        "ob_room_data_polish.js"
        not in source
    )


def test_normal_dashboard_no_longer_loads_obux027_atmosphere():
    source = text(DASH)

    assert (
        "ob_atmosphere.css"
        not in source
    )


def test_product_policy_is_fresh_and_early():
    source = text(DASH)

    assert (
        "ob_product_surface_policy.js?v=obux086090"
        in source
    )

    assert (
        source.index(
            "ob_product_surface_policy.js?v=obux086090"
        )
        < source.index(
            "<body"
        )
    )


def test_changed_runtime_assets_have_new_cache_identity():
    source = text(DASH)

    for token in [
        "ob_interchangeable_themes.css?v=obux081085",
        "ob_theme_switcher.js?v=obux081085",
        "ob_beta_surface_cleanup.js?v=obux081085",
        "ob_session_arrival.js') }}?v=obux071075",
    ]:
        assert token in source


def test_product_policy_denies_legacy_mission_ui_on_all_ob_product_routes():
    source = text(POLICY)

    assert (
        "missionUiAllowed"
        in source
    )

    assert (
        "return !isObProductRoute();"
        in source
    )

    assert (
        '"#obMissionBar"'
        in source
    )


def test_product_policy_denies_v27_for_all_ob_product_routes():
    source = text(POLICY)

    assert (
        "v27UiAllowed"
        in source
    )

    assert (
        'startsWith(\n        "/ob/"'
        in source
    )

    assert (
        '"#obRoomDataPolishPanel"'
        in source
    )

    assert (
        '"obEngineFeedAdapterUpdated"'
        in source
    )


def test_mission_renderer_source_gate_precedes_mission_definitions():
    source = text(MISSIONS)

    gate = source.index(
        "ownerDashboardSurface"
    )

    definitions = source.index(
        "const missionAccounts"
    )

    assert gate < definitions

    assert (
        '=== "/ob/owner-dashboard"'
        in source
    )

    assert (
        "mission_accounts_owner_dashboard_only"
        in source
    )


def test_v27_source_gate_precedes_original_renderer():
    source = text(V27)

    gate = source.index(
        "productSurface"
    )

    renderer = source.index(
        "function currentRoomKey"
    )

    assert gate < renderer

    assert (
        'startsWith(\n        "/ob/"'
        in source
    )

    assert (
        "v27_proof_ui_not_allowed_on_ob_product_routes"
        in source
    )


def test_v27_historical_renderer_still_exists_for_non_product_proof_history():
    source = text(V27)

    assert (
        "OB_V27_ROOM_LEVEL_REAL_DATA_POLISH"
        in source
    )

    assert (
        "Room-Level Data Polish · V27"
        in source
    )

    assert (
        "insertPanel"
        in source
    )


def test_dashboard_theme_owns_required_sky_geometry():
    source = text(THEMES)

    assert (
        "OBUX074_DASHBOARD_THEME_OWNS_SKY_GEOMETRY"
        in source
    )

    for token in [
        '.ob-sky {',
        ".ob-sky::before",
        ".ob-sky__weather",
        ".ob-sky__horizon",
        ".ob-sky__grid",
        "@keyframes obThemeStarsDrift",
        "@keyframes obThemeWeatherDrift",
    ]:
        assert token in source


def test_dashboard_layout_remains_untouched():
    source = text(DASH)

    for token in [
        "SOULAANA · RIGHT NOW",
        "SINCE YOU WERE HERE",
        "YOUR ACTIVITY",
        "MARKET NOW",
        "YOUR OPERATING LOOP",
        "MY OB",
    ]:
        assert token in source


def test_normal_dashboard_still_has_no_mission_account_dependency():
    source = text(DASH).lower()

    for token in [
        "mission_accounts",
        "ob_mission_account",
        "current mission account",
    ]:
        assert token not in source


def test_no_execution_capability_was_added():
    source = (
        text(POLICY)
        + "\n"
        + text(MISSIONS)
        + "\n"
        + text(V27)
        + "\n"
        + text(THEMES)
    )

    for forbidden in [
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "broker.submit",
    ]:
        assert forbidden not in source
