
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

DASH = ROOT / "web/templates/dashboard.html"
OWNER_DASH = ROOT / "web/templates/owner_dashboard.html"
OWNER_CONSOLE = ROOT / "web/templates/owner_console.html"
APP = ROOT / "web/app.py"
SESSION = ROOT / "web/static/ob/ob_session_state.js"
ARRIVAL = ROOT / "web/static/ob/ob_session_arrival.js"
PROJECTION = ROOT / "web/static/ob/ob_dashboard_projection.js"
DASH_JS = ROOT / "web/static/ob/ob_dashboard.js"
GLOBAL = ROOT / "web/static/ob/ob_global_session_shell.js"
CSS = ROOT / "web/static/ob/ob_dashboard_obux.css"


def text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def compact(value):
    return re.sub(r"\s+", "", value)


def test_obux056_normal_dashboard_identity_survives_replacement():
    source = text(DASH)

    for token in [
        'data-ob-surface="user-dashboard"',
        'data-ob-dashboard-role="normal"',
        'data-ob-owner-dashboard="false"',
        'data-ob-owner-console="false"',
        'data-ob-build="OBUX091-095"',
    ]:
        assert token in source


def test_obux056_owner_surfaces_remain_separate():
    normal = text(DASH)

    assert normal != text(OWNER_DASH)
    assert normal != text(OWNER_CONSOLE)


def test_obux056_legacy_mission_account_dependency_remains_absent():
    source = text(DASH).lower()

    for token in [
        "ob_mission_accounts.js",
        "ob_account_experience.js",
        "current mission account",
        "mission_accounts",
    ]:
        assert token not in source


def test_obux057_user_projection_is_now_market_learning_not_account_snapshot():
    source = text(PROJECTION)

    assert (
        "OBUX091_095_USER_DASHBOARD_PROJECTION"
        in source
    )

    assert (
        "/ob/account-experience.json"
        not in source
    )

    for token in [
        "market_glance",
        "neutralSymbolFacts",
        "paperState",
        "recentReview",
        "owner_candidate_payloads",
    ]:
        assert token in source


def test_obux057_no_fake_market_fallbacks():
    combined = (
        text(PROJECTION)
        + "\n"
        + text(DASH_JS)
    )

    assert "Math.random" not in combined
    assert "fake" not in text(PROJECTION).lower()


def test_obux058_session_and_arrival_system_preserved():
    combined = (
        text(SESSION)
        + "\n"
        + text(ARRIVAL)
    )

    for token in [
        "sopAcknowledgedVersion",
        "selectedMode",
        "lastSafeRoute",
        "notificationReadiness",
        "Skip for now",
        "sessionStorage",
    ]:
        assert token in combined


def test_obux059_guided_product_flow_still_reaches_market_map():
    combined = (
        text(ARRIVAL)
        + "\n"
        + text(DASH_JS)
        + "\n"
        + text(GLOBAL)
    )

    assert "Market Map" in combined
    assert "Take me to Market Map" in combined
    assert "No proof pages" in combined


def test_obux059_global_shell_preserves_tower_return_and_signout():
    source = text(GLOBAL)

    assert "/tower/return/observatory" in source
    assert "Back to Tower" in source
    assert "Sign out of OB" in source


def test_obux059_live_auto_remains_locked():
    combined = (
        text(GLOBAL)
        + "\n"
        + text(PROJECTION)
        + "\n"
        + text(DASH)
    )

    assert "Live Auto" in combined
    assert "automatic_execution" in combined


def test_obux060_old_dashboard_ui_stack_not_loaded():
    source = text(DASH)

    for token in [
        "ob_dashboard_simplification_obux.js",
        "ob_account_experience.js",
        "ob_mission_accounts.js",
        "ob_market_data.js",
        "ob_owner_dashboard_contract.js",
    ]:
        assert token not in source


def test_obux060_no_direct_execution_code():
    source = "\n".join([
        text(SESSION),
        text(ARRIVAL),
        text(PROJECTION),
        text(DASH_JS),
        text(GLOBAL),
    ])

    for pattern in [
        r"\bplaceOrder\s*\(",
        r"\bsubmitOrder\s*\(",
        r"\bexecuteTrade\s*\(",
        r"\bautoExecute\s*\(",
    ]:
        assert not re.search(
            pattern,
            source,
            re.I,
        )


def test_obux060_accessibility_and_reduced_motion():
    source = (
        text(CSS)
        + "\n"
        + text(ARRIVAL)
    )

    assert "prefers-reduced-motion" in source
    assert "focus-visible" in source
    assert "aria-modal" in source
