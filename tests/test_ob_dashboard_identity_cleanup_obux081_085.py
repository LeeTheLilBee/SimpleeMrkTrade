
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DASH = ROOT / "web/templates/dashboard.html"
OWNER = ROOT / "web/templates/owner_dashboard.html"
THEMES = ROOT / "web/static/ob/ob_interchangeable_themes.css"
SWITCHER = ROOT / "web/static/ob/ob_theme_switcher.js"
SETTINGS = ROOT / "web/static/ob/ob_notifications_settings.js"
POLICY = ROOT / "web/static/ob/ob_product_surface_policy.js"
CLEANUP = ROOT / "web/static/ob/ob_beta_surface_cleanup.js"


def text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def test_obux081_mission_setting_remains_retired():
    source = text(SETTINGS)

    for forbidden in [
        "missionSettingsAllowed",
        "Mission bar",
        "missionLayout",
    ]:
        assert forbidden not in source


def test_obux081_normal_dashboard_has_no_mission_runtime():
    source = text(DASH).lower()

    assert "ob_mission_accounts.js" not in source
    assert "current mission account" not in source


def test_obux082_first_paint_theme_still_precedes_stylesheet():
    source = text(DASH)

    bootstrap = source.index(
        "First-paint Observatory theme authority"
    )

    stylesheet = source.index(
        'rel="stylesheet"'
    )

    assert bootstrap < stylesheet


def test_obux083_observatory_palette_remains():
    source = (
        text(THEMES)
        + "\n"
        + text(SWITCHER)
    )

    for token in [
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
        assert token in source


def test_obux084_dashboard_product_policy_remains_fresh():
    source = text(DASH)

    assert (
        "ob_product_surface_policy.js?v=obux086090"
        in source
    )


def test_obux085_both_dashboard_builds_are_current():
    assert (
        'data-ob-build="OBUX091-095"'
        in text(DASH)
    )

    assert (
        'data-ob-build="OBUX091-095"'
        in text(OWNER)
    )


def test_obux085_new_user_dashboard_is_not_old_product_wall():
    source = text(DASH)

    for required in [
        "SOULAANA · MARKET BRIEFING",
        "MARKET GLANCE",
        "More from your Observatory",
    ]:
        assert required in source


def test_obux085_live_auto_remains_locked():
    combined = (
        text(DASH)
        + "\n"
        + text(OWNER)
        + "\n"
        + text(CLEANUP)
    )

    assert "Live Auto" in combined
    assert "Locked" in combined
