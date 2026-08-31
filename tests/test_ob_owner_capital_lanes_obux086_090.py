
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

DASH = ROOT / "web/templates/dashboard.html"
OWNER_DASH = ROOT / "web/templates/owner_dashboard.html"
POLICY = ROOT / "web/static/ob/ob_product_surface_policy.js"
SETTINGS = ROOT / "web/static/ob/ob_notifications_settings.js"
OWNER_CONTRACT = ROOT / "web/static/ob/ob_owner_dashboard_contract.js"
OWNER_SOULAANA = ROOT / "web/static/ob/ob_owner_dashboard_soulaana.js"
OWNER_JS = ROOT / "web/static/ob/ob_owner_dashboard.js"
OWNER_CSS = ROOT / "web/static/ob/ob_owner_dashboard.css"


CANONICAL = [
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


def compact(value):
    return re.sub(
        r"\s+",
        "",
        value,
    )


def test_obux086_no_canonical_product_loads_legacy_mission_runtime():
    forbidden = [
        "ob_mission_accounts.js",
        "ob_mission_account_capital_rule_rehearsal_overlay.js",
        "ob_account_experience.js",
    ]

    for path in CANONICAL:
        source = text(path)

        for token in forbidden:
            assert token not in source, (
                f"{token} still loaded by {path.name}"
            )


def test_obux086_shared_settings_still_have_no_mission_display_setting():
    source = text(SETTINGS)

    for forbidden in [
        "missionSettingsAllowed",
        "Mission bar",
        "missionLayout",
    ]:
        assert forbidden not in source


def test_obux087_six_owner_capital_lanes_remain_defined():
    source = compact(
        text(OWNER_CONTRACT)
    )

    for lane in [
        'lane_id:"trust"',
        'lane_id:"personal"',
        'lane_id:"simplee_world"',
        'lane_id:"atm"',
        'lane_id:"apartment"',
        'lane_id:"proof_demo"',
    ]:
        assert lane in source

    assert "capital_lanes_owner_dashboard_only:true" in source


def test_obux087_capital_lane_boundary_remains_context_only():
    source = compact(
        text(OWNER_CONTRACT)
    )

    for token in [
        "lane_selection_changes_context_only:true",
        "broker_order_submission_enabled:false",
        "real_capital_movement_enabled:false",
        "automatic_contract_selection_enabled:false",
        "auto_execution_enabled:false",
        "live_auto_locked:true",
    ]:
        assert token in source


def test_obux088_capital_lanes_are_now_secondary_owner_context():
    source = text(OWNER_JS)

    for token in [
        "CAPITAL LANES",
        "CURRENT CAPITAL LANE",
        "Capital context — secondary.",
        "One lane at a time.",
        "Enter this lane",
        "ob.owner.capital-lane.v1",
    ]:
        assert token in source


def test_obux088_clicking_lane_still_opens_detail_not_context_switch():
    source = text(OWNER_JS)

    # Inspect the actual rendered lane-button event wiring.
    lane_marker = (
        '"[data-capital-lane-open]"'
    )

    lane_event_at = source.rfind(
        lane_marker
    )

    assert lane_event_at >= 0

    lane_event_end = source.find(
        "const noLane =",
        lane_event_at,
    )

    assert lane_event_end > lane_event_at

    lane_handler = source[
        lane_event_at:
        lane_event_end
    ]

    # Clicking a Capital Lane opens details only.
    assert "openLaneDrawer(" in lane_handler
    assert "writeSelectedLane(" not in lane_handler

    # Do not assume where the explicit Enter handler appears
    # relative to the rendered lane-button handler in the file.
    write_call_at = source.rfind(
        "writeSelectedLane("
    )

    assert write_call_at >= 0

    enter_control_at = source.rfind(
        '"obCapitalLaneEnter"',
        0,
        write_call_at,
    )

    assert enter_control_at >= 0

    enter_handler = source[
        enter_control_at:
        min(
            len(source),
            write_call_at + 500,
        )
    ]

    # Context changes only after explicit Enter-this-lane.
    assert "writeSelectedLane(" in enter_handler
    assert "lane.lane_id" in enter_handler

    assert (
        "Clicking a lane never switches owner context"
        in source
    )


def test_obux088_owner_drawer_has_keyboard_escape():
    source = text(OWNER_JS)

    assert "trapFocus" in source
    assert 'event.key === "Escape"' in source
    assert 'aria-modal' in source


def test_obux088_adhd_depth_stays_collapsed():
    source = text(OWNER_JS)

    for token in [
        "Only the top three.",
        "More owner intelligence",
        "Show me why",
        "Three things max.",
    ]:
        assert token in source


def test_obux088_accessibility_and_reduced_motion():
    source = text(OWNER_CSS)

    assert "focus-visible" in source
    assert "prefers-reduced-motion" in source
    assert "max-width: 920px" in source
    assert "max-width: 620px" in source


def test_obux089_normal_dashboard_has_no_account_or_owner_chrome():
    source = text(DASH)

    for forbidden in [
        "Account snapshot",
        "Your OB account",
        "CAPITAL LANES",
        "TODAY’S EDGE",
        "OWNER RESEARCH",
    ]:
        assert forbidden not in source


def test_obux090_owner_dashboard_assets_are_new_build():
    source = text(OWNER_DASH)

    for token in [
        'data-ob-build="OBUX091-095"',
        "ob_owner_dashboard.css') }}?v=obux091095",
        "ob_owner_dashboard_contract.js') }}?v=obux091095",
        "ob_owner_dashboard_soulaana.js') }}?v=obux091095",
        "ob_owner_dashboard.js') }}?v=obux091095",
        "data-ob-owner-dashboard-role=\"owner-only-active\"",
    ]:
        assert token in source


def test_obux090_no_execution_capability_added():
    combined = "\n".join([
        text(OWNER_CONTRACT),
        text(OWNER_JS),
        text(OWNER_SOULAANA),
        text(POLICY),
        text(SETTINGS),
    ])

    for forbidden in [
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "broker.submit(",
    ]:
        assert forbidden not in combined
