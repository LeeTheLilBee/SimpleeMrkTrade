
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CSS = ROOT / "web/static/ob/ob_interchangeable_themes.css"
THEME = ROOT / "web/static/ob/ob_theme_switcher.js"
CLEANUP = ROOT / "web/static/ob/ob_beta_surface_cleanup.js"
DASH = ROOT / "web/templates/dashboard.html"
DASH_CSS = ROOT / "web/static/ob/ob_dashboard_obux.css"
OWNER_CSS = ROOT / "web/static/ob/ob_owner_dashboard.css"


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
    source = text(CSS) + text(THEME)

    for token in [
        "#050809",
        "#0D1717",
        "#12302D",
        "#39BFA5",
        "#A7E8D8",
        "#D8E2E0",
    ]:
        assert token in source


def test_default_is_aurora_ink():
    assert '"aurora-ink"' in text(THEME)


def test_theme_persistence_is_appearance_only():
    source = text(THEME)

    assert "localStorage" in source
    assert "ob.appearance.theme.v2" in source

    for forbidden in [
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "rankContract(",
    ]:
        assert forbidden not in source


def test_dashboard_layout_is_new_attention_first_surface():
    source = text(DASH)

    for token in [
        "SOULAANA · MARKET BRIEFING",
        "MARKET GLANCE",
        "Three things max.",
        "More from your Observatory",
    ]:
        assert token in source


def test_no_bright_cyan_blue_palette_added():
    source = (
        text(CSS)
        + text(DASH_CSS)
        + text(OWNER_CSS)
    ).lower()

    for forbidden in [
        "#7ffcff",
        "#8fc4ff",
        "rgb(0, 191, 255)",
    ]:
        assert forbidden not in source


def test_reduced_motion_exists_on_both_new_dashboards():
    assert "prefers-reduced-motion" in text(DASH_CSS)
    assert "prefers-reduced-motion" in text(OWNER_CSS)


def test_beta_cleanup_still_rejects_legacy_noise():
    source = text(CLEANUP)

    assert "#obMissionBar" in source
    assert "#obRoomDataPolishPanel" in source
    assert "MutationObserver" in source
