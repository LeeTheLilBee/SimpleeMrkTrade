
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DASH = ROOT / "web/templates/dashboard.html"
POLICY = ROOT / "web/static/ob/ob_product_surface_policy.js"
MISSIONS = ROOT / "web/static/ob/ob_mission_accounts.js"
V27 = ROOT / "web/static/ob/ob_room_data_polish.js"
THEMES = ROOT / "web/static/ob/ob_interchangeable_themes.css"


def text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def test_dashboard_is_current_obux091_095_surface():
    assert (
        'data-ob-build="OBUX091-095"'
        in text(DASH)
    )


def test_normal_dashboard_does_not_load_mission_script():
    assert (
        "ob_mission_accounts.js"
        not in text(DASH)
    )


def test_normal_dashboard_does_not_load_v27_renderer():
    assert (
        "ob_room_data_polish.js"
        not in text(DASH)
    )


def test_product_policy_is_still_early():
    source = text(DASH)

    token = (
        "ob_product_surface_policy.js?v=obux086090"
    )

    assert token in source

    assert (
        source.index(token)
        < source.index("<body")
    )


def test_legacy_mission_product_ui_remains_denied():
    source = text(POLICY)

    assert "missionUiAllowed" in source
    assert "return !isObProductRoute();" in source
    assert '"#obMissionBar"' in source


def test_v27_historical_renderer_still_not_loaded_into_product():
    source = text(V27)

    assert (
        "OB_V27_ROOM_LEVEL_REAL_DATA_POLISH"
        in source
    )

    assert (
        "v27_proof_ui_not_allowed_on_ob_product_routes"
        in source
    )


def test_dashboard_layout_is_attention_first_not_legacy_wall():
    source = text(DASH)

    for required in [
        "SOULAANA · MARKET BRIEFING",
        "MARKET GLANCE",
        "Three things max.",
    ]:
        assert required in source

    for forbidden in [
        "SINCE YOU WERE HERE",
        "YOUR ACTIVITY",
        "YOUR OPERATING LOOP",
        "MY OB",
    ]:
        assert forbidden not in source


def test_historical_mission_source_cannot_create_execution():
    source = (
        text(MISSIONS)
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
