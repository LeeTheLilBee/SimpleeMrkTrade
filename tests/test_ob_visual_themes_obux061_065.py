from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CSS = (
    ROOT
    / "web/static/ob/ob_interchangeable_themes.css"
)

THEME = (
    ROOT
    / "web/static/ob/ob_theme_switcher.js"
)

CLEANUP = (
    ROOT
    / "web/static/ob/ob_beta_surface_cleanup.js"
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


def text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def test_three_interchangeable_themes_exist():
    source = text(THEME)

    for token in [
        "aurora-ink",
        "deep-field",
        "lunar-sage",
        "OBThemeSwitcher",
    ]:
        assert token in source


def test_exact_palette_values_exist():
    source = (
        text(CSS)
        + text(THEME)
    )

    for token in [
        "#050809",
        "#0D1717",
        "#12302D",
        "#39BFA5",
        "#A7E8D8",
        "#D8E2E0",

        "#040707",
        "#0A1212",
        "#102421",
        "#2B9B88",
        "#8DD8C8",
        "#DDE8E4",

        "#070A09",
        "#111816",
        "#1B2824",
        "#78A894",
        "#BFD8CE",
        "#E8EEEB",
    ]:
        assert token in source


def test_default_is_aurora_ink():
    assert (
        'const DEFAULT ='
        in text(THEME)
    )

    assert (
        '"aurora-ink"'
        in text(THEME)
    )


def test_theme_is_persisted_and_appearance_only():
    source = text(THEME)

    assert "localStorage" in source
    assert "ob.appearance.theme.v2" in source

    for forbidden in [
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "rankContract(",
        "selectedMissionAccount",
    ]:
        assert forbidden not in source


def test_dashboard_layout_is_preserved():
    source = text(DASH)

    for token in [
        "SOULAANA · RIGHT NOW",
        "Account snapshot",
        "SINCE YOU WERE HERE",
        "YOUR ACTIVITY",
        "MARKET NOW",
        "YOUR OPERATING LOOP",
        "MY OB",
    ]:
        assert token in source


def test_dashboard_header_button_cluster_removed():
    assert (
        "ob-user-header-actions"
        not in text(DASH)
    )


def test_room_polish_is_rejected():
    source = text(CLEANUP)

    assert "#obRoomDataPolishPanel" in source
    assert ".ob-room-polish-panel" in source
    assert "MutationObserver" in source
    assert "purgeLegacyProductNoise" in source


def test_mission_bar_is_rejected_from_beta_product_surface():
    source = text(CLEANUP)

    assert "#obMissionBar" in source
    assert ".ob-mission-bar" in source


def test_top_bars_are_not_permanent_on_beta_surface():
    source = text(CSS)

    assert (
        "body.ob-beta-product-surface #obRouteBar"
        in source
    )

    assert (
        "body.ob-beta-product-surface #obGlobalSessionBar"
        in source
    )


def test_compact_drawer_has_controls():
    source = text(CLEANUP)

    for token in [
        "Appearance",
        "Send beta feedback",
        "Beta Guide",
        "What Changed",
        "Back to Tower",
        "Sign out of OB",
    ]:
        assert token in source


def test_owner_surfaces_do_not_receive_beta_cleanup_class():
    source = text(CLEANUP)

    assert (
        'path().includes(\n        "owner-dashboard"'
        in source
    )

    assert (
        'path().includes(\n        "owner-console"'
        in source
    )

    assert (
        "return !isOwnerSurface();"
        in source
    )


def test_all_canonical_templates_load_assets():
    for path in CORE:
        source = text(path)

        assert (
            "ob_interchangeable_themes.css"
            in source
        ), path

        assert (
            "ob_theme_switcher.js"
            in source
        ), path

        assert (
            "ob_beta_surface_cleanup.js"
            in source
        ), path


def test_no_bright_cyan_blue_palette_added():
    source = text(CSS).lower()

    for forbidden in [
        "#7ffcff",
        "#8fc4ff",
        "rgb(0, 191, 255)",
    ]:
        assert forbidden not in source


def test_tower_and_live_auto_state_remain_available():
    source = text(CLEANUP)

    assert "Tower" in source
    assert "Protected" in source
    assert "Live Auto" in source
    assert "Locked" in source
