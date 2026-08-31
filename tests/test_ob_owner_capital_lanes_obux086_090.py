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

OWNER_DASH = (
    ROOT
    / "web/templates/owner_dashboard.html"
)

POLICY = (
    ROOT
    / "web/static/ob/ob_product_surface_policy.js"
)

SETTINGS = (
    ROOT
    / "web/static/ob/ob_notifications_settings.js"
)

OWNER_CONTRACT = (
    ROOT
    / "web/static/ob/ob_owner_dashboard_contract.js"
)

OWNER_SOULAANA = (
    ROOT
    / "web/static/ob/ob_owner_dashboard_soulaana.js"
)

OWNER_JS = (
    ROOT
    / "web/static/ob/ob_owner_dashboard.js"
)

OWNER_CSS = (
    ROOT
    / "web/static/ob/ob_owner_dashboard.css"
)


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


def test_obux086_product_policy_denies_legacy_mission_ui_everywhere():
    source = text(POLICY)

    assert (
        "return !isObProductRoute();"
        in source
    )

    for token in [
        "#obMissionBar",
        "#obAccountExperiencePanel",
        "data-ob-mission-account-enabled",
        "data-ob-giant-pack-001-account-experience",
    ]:
        assert token in source


def test_obux086_shared_settings_have_no_mission_display_setting():
    source = text(SETTINGS)

    for forbidden in [
        "missionSettingsAllowed",
        "Mission bar",
        "missionLayout",
        "obSettingMissionLayout",
    ]:
        assert forbidden not in source


def test_obux087_owner_contract_owns_six_capital_lanes():
    source = text(OWNER_CONTRACT)

    for lane in [
        '"trust"',
        '"personal"',
        '"simplee_world"',
        '"atm"',
        '"apartment"',
        '"proof_demo"',
    ]:
        assert lane in source

    assert (
        "capital_lanes:"
        in source
    )

    assert (
        "capital_lanes_owner_dashboard_only"
        in source
    )


def test_obux087_owner_contract_does_not_consume_generic_account_experience():
    source = text(OWNER_CONTRACT)

    assert (
        "/ob/account-experience.json"
        not in source
    )

    assert (
        "owner_mission_accounts"
        not in source
    )

    assert (
        "mission_sky"
        not in source
    )


def test_obux087_owner_contract_is_context_only_and_fail_closed():
    source = text(OWNER_CONTRACT)

    for token in [
        "lane_selection_changes_context_only",
        "broker_order_submission_enabled",
        "real_capital_movement_enabled",
        "automatic_contract_selection_enabled",
        "auto_execution_enabled",
        "live_auto_locked",
    ]:
        assert token in source

    for forbidden in [
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "broker.submit(",
    ]:
        assert forbidden not in source


def test_obux088_owner_dashboard_uses_capital_lane_language():
    source = (
        text(OWNER_JS)
        + "\n"
        + text(OWNER_SOULAANA)
    )

    for token in [
        "CAPITAL LANES",
        "CURRENT CAPITAL LANE",
        "One lane at a time.",
        "Enter this lane",
        "ob.owner.capital-lane.v1",
    ]:
        assert token in source


def test_obux088_clicking_lane_opens_details_not_selection():
    source = text(OWNER_JS)

    # Ordinary lane-button handling must open details only.
    click_marker = (
        "DETAIL ONLY.\n"
        "                No automatic context switch."
    )

    click_start = source.index(
        click_marker
    )

    click_end = source.index(
        'document.body.setAttribute(',
        click_start,
    )

    click_handler = source[
        click_start:click_end
    ]

    assert (
        "openLaneDrawer("
        in click_handler
    )

    assert (
        "writeSelectedLane("
        not in click_handler
    )

    # Selection is allowed only inside the explicit
    # Enter-this-lane action handler.
    enter_start = source.index(
        'getElementById(\n        "obCapitalLaneEnter"'
    )

    enter_end = source.index(
        "backdrop.addEventListener(",
        enter_start,
    )

    enter_handler = source[
        enter_start:enter_end
    ]

    assert (
        "writeSelectedLane("
        in enter_handler
    )

    assert (
        "lane.lane_id"
        in enter_handler
    )

    assert (
        "Clicking a lane never switches owner context"
        in source
    )


def test_obux088_one_drawer_and_keyboard_escape():
    source = text(OWNER_JS)

    for token in [
        "closeLaneDrawer();",
        "obCapitalLaneDrawerBackdrop",
        'event.key\n          === "Escape"',
        'aria-modal',
        "trapFocus",
    ]:
        assert token in source


def test_obux088_adhd_surface_keeps_depth_collapsed():
    source = text(OWNER_JS)

    assert (
        "Only the top three."
        in source
    )

    assert (
        "More owner intelligence"
        in source
    )

    assert (
        "Show me why"
        in source
    )

    assert (
        ".slice(\n              0,\n              3"
        in source
        or ".slice(\n              0,\n              3\n"
        in source
    )


def test_obux088_accessibility_and_reduced_motion():
    source = text(OWNER_CSS)

    for token in [
        "focus-visible",
        "prefers-reduced-motion",
        "max-width: 920px",
        "max-width: 620px",
    ]:
        assert token in source


def test_obux088_owner_dashboard_gets_fresh_assets_and_first_paint_theme():
    source = text(OWNER_DASH)

    for token in [
        "data-ob-owner-capital-lanes",
        "ob_product_surface_policy.js?v=obux086090",
        "ob_owner_dashboard.css') }}?v=obux086090",
        "ob_owner_dashboard_contract.js') }}?v=obux086090",
        "ob_owner_dashboard_soulaana.js') }}?v=obux086090",
        "ob_owner_dashboard.js') }}?v=obux086090",
        "ob.appearance.theme.v2",
        "aurora-ink",
    ]:
        assert token in source


def test_obux089_normal_dashboard_has_no_account_chrome():
    source = text(DASH)

    for forbidden in [
        "Account snapshot",
        "Your OB account",
        'class="ob-account-snapshot"',
        'id="obAccountSnapshot"',
        'id="obAccountSource"',
    ]:
        assert forbidden not in source


def test_obux089_normal_dashboard_still_has_core_intelligence():
    source = text(DASH)

    for required in [
        "SOULAANA · RIGHT NOW",
        "SINCE YOU WERE HERE",
        "YOUR ACTIVITY",
        "MARKET NOW",
        "YOUR OPERATING LOOP",
        "MY OB",
    ]:
        assert required in source


def test_obux090_dashboard_build_marker_current():
    assert (
        'data-ob-build="OBUX086-090"'
        in text(DASH)
    )


def test_obux090_owner_only_boundary_is_explicit():
    template = text(OWNER_DASH)
    contract = text(OWNER_CONTRACT)

    assert (
        'data-ob-owner-dashboard-role="owner-only-active"'
        in template
    )

    assert (
        "owner_only:"
        in contract
    )

    assert (
        "non_owner_capital_lane_delivery"
        in contract
    )


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

    assert (
        "Live Auto Locked"
        in text(OWNER_DASH)
        or "live_auto_locked"
        in combined
    )
