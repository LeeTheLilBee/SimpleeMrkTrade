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

CORE = [
    ROOT / "web/templates/dashboard.html",
    ROOT / "web/templates/market_map.html",
    ROOT / "web/templates/symbol_page.html",
    ROOT / "web/templates/trade_center.html",
    ROOT / "web/templates/review_center.html",
    ROOT / "web/templates/owner_dashboard.html",
    ROOT / "web/templates/owner_console.html",
]

THEMES = (
    ROOT
    / "web/static/ob/ob_interchangeable_themes.css"
)

SWITCHER = (
    ROOT
    / "web/static/ob/ob_theme_switcher.js"
)

SETTINGS = (
    ROOT
    / "web/static/ob/ob_notifications_settings.js"
)

POLICY = (
    ROOT
    / "web/static/ob/ob_product_surface_policy.js"
)

CLEANUP = (
    ROOT
    / "web/static/ob/ob_beta_surface_cleanup.js"
)


def text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def test_obux081_dashboard_has_no_mission_renderer_dependency():
    source = text(DASH).lower()

    for forbidden in [
        "ob_mission_accounts.js",
        "current mission account",
        "mission account switcher",
    ]:
        assert forbidden not in source


def test_obux081_mission_settings_are_owner_dashboard_only():
    source = text(SETTINGS)

    assert (
        "function missionSettingsAllowed()"
        in source
    )

    assert (
        '=== "/ob/owner-dashboard"'
        in source
    )

    normalized = " ".join(
        source.split()
    )

    assert (
        'document.body.removeAttribute( '
        '"data-ob-mission-layout" );'
        in normalized
    )

    assert (
        "missionSettingsAllowed()\n"
        "            ? settingSelect("
        in source
    )


def test_obux081_policy_removes_mission_layout_state():
    source = text(POLICY)

    assert (
        '"data-ob-mission-layout"'
        in source
    )

    assert (
        '"data-ob-mission"'
        in source
    )

    assert (
        '"/ob/owner-dashboard"'
        in source
    )


def test_obux081_beta_cleanup_removes_mission_state():
    source = text(CLEANUP)

    assert (
        '"#obMissionBar"'
        in source
    )

    assert (
        '".ob-mission-bar"'
        in source
    )

    assert (
        '"data-ob-mission-layout"'
        in source
    )


def test_obux082_dashboard_applies_theme_before_first_stylesheet():
    source = text(DASH)

    bootstrap = source.index(
        "OBUX082 — FIRST-PAINT OBSERVATORY THEME AUTHORITY"
    )

    first_stylesheet = source.index(
        'rel="stylesheet"'
    )

    assert bootstrap < first_stylesheet

    assert (
        '"ob.appearance.theme.v2"'
        in source
    )

    assert (
        '"aurora-ink"'
        in source
    )


def test_obux083_observatory_has_new_color_identity():
    source = (
        text(THEMES)
        + "\n"
        + text(SWITCHER)
    )

    for required in [
        "aurora-ink",
        "deep-field",
        "lunar-sage",
        "#050809",
        "#0D1717",
        "#12302D",
        "#39BFA5",
        "#A7E8D8",
        "#D8E2E0",
    ]:
        assert required in source


def test_obux083_old_tower_like_default_palette_removed():
    source = (
        text(THEMES)
        + "\n"
        + text(SWITCHER)
    ).lower()

    for forbidden in [
        "obsidian-plum",
        "velvet-night",
        "eclipse-gold",
        "#6c4d8e",
        "#b58a45",
        "#8e79b7",
        "#c49a57",
        "#74618f",
        "#d0a45d",
    ]:
        assert forbidden not in source


def test_obux083_new_theme_switcher_ignores_old_storage_key():
    source = text(SWITCHER)

    assert (
        '"ob.appearance.theme.v2"'
        in source
    )

    assert (
        '"ob.appearance.theme.v1"'
        not in source
    )

    assert (
        'const DEFAULT =\n    "aurora-ink";'
        in source
    )


def test_obux084_all_canonical_rooms_have_fresh_theme_assets():
    for path in CORE:
        source = text(path)

        for token in [
            "ob_interchangeable_themes.css?v=obux081085",
            "ob_theme_switcher.js?v=obux081085",
            "ob_beta_surface_cleanup.js?v=obux081085",
        ]:
            assert token in source, (
                f"{token} missing from {path.name}"
            )


def test_obux084_dashboard_has_fresh_product_policy():
    source = text(DASH)

    assert (
        "ob_product_surface_policy.js?v=obux081085"
        in source
    )

    assert (
        source.index(
            "ob_product_surface_policy.js?v=obux081085"
        )
        < source.index(
            "<body"
        )
    )


def test_obux085_dashboard_layout_remains_product_dashboard():
    source = text(DASH)

    for required in [
        "Account snapshot",
        "SOULAANA · RIGHT NOW",
        "SINCE YOU WERE HERE",
        "YOUR ACTIVITY",
        "MARKET NOW",
        "YOUR OPERATING LOOP",
        "MY OB",
    ]:
        assert required in source


def test_obux085_dashboard_build_marker_current():
    assert (
        'data-ob-build="OBUX081-085"'
        in text(DASH)
    )


def test_obux085_no_execution_capability_added():
    source = "\n".join(
        [
            text(THEMES),
            text(SWITCHER),
            text(SETTINGS),
            text(POLICY),
            text(CLEANUP),
            text(DASH),
        ]
    )

    for forbidden in [
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "broker.submit(",
    ]:
        assert forbidden not in source


def test_obux085_live_auto_remains_locked():
    combined = (
        text(DASH)
        + "\n"
        + text(CLEANUP)
    )

    assert (
        "Live Auto"
        in combined
    )

    assert (
        "Locked"
        in combined
    )
