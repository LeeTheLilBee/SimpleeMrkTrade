from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


DASH = (
    ROOT
    / "web/templates/dashboard.html"
)

OWNER_DASH = (
    ROOT
    / "web/templates/owner_dashboard.html"
)

OWNER_CONSOLE = (
    ROOT
    / "web/templates/owner_console.html"
)

APP = (
    ROOT
    / "web/app.py"
)

SESSION = (
    ROOT
    / "web/static/ob/ob_session_state.js"
)

ARRIVAL = (
    ROOT
    / "web/static/ob/ob_session_arrival.js"
)

PROJECTION = (
    ROOT
    / "web/static/ob/ob_dashboard_projection.js"
)

DASH_JS = (
    ROOT
    / "web/static/ob/ob_dashboard.js"
)

GLOBAL = (
    ROOT
    / "web/static/ob/ob_global_session_shell.js"
)

CSS = (
    ROOT
    / "web/static/ob/ob_dashboard_obux.css"
)


CORE_TEMPLATES = [
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


def test_obux056_is_normal_user_dashboard():
    source = text(DASH)

    assert (
        'data-ob-surface="user-dashboard"'
        in source
    )

    assert (
        'data-ob-dashboard-role="normal"'
        in source
    )

    assert (
        'data-ob-owner-dashboard="false"'
        in source
    )

    assert (
        'data-ob-owner-console="false"'
        in source
    )

    for phrase in [
        "SINCE YOU WERE HERE",
        "YOUR ACTIVITY",
        "MARKET NOW",
        "YOUR OPERATING LOOP",
        "MY OB",
    ]:
        assert phrase in source


def test_obux056_no_mission_account_dependency():
    source = text(DASH).lower()

    assert (
        "ob_mission_accounts.js"
        not in source
    )

    assert (
        "ob_mission_account"
        not in source
    )

    assert (
        "mission_accounts"
        not in source
    )


def test_obux056_owner_surfaces_remain_separate():
    normal = text(DASH)

    assert normal != text(OWNER_DASH)

    assert normal != text(OWNER_CONSOLE)

    assert (
        "owner_dashboard"
        not in normal.lower()
    )


def test_obux056_canonical_assets_loaded():
    source = text(DASH)

    for token in [
        "ob_session_state.js",
        "ob_dashboard_projection.js",
        "ob_session_arrival.js",
        "ob_dashboard.js",
        "ob_nav_shell.js",
        "ob_global_session_shell.js",
        "ob_dashboard_obux.css",
    ]:
        assert token in source


def test_obux057_projection_does_not_consume_missions():
    source = text(PROJECTION)

    assert (
        "missionAccountsOnUserDashboard"
        in source
    )

    assert (
        "missionAccountsOnUserDashboard:\n          false"
        in source
    )

    assert (
        "payload.mission_accounts"
        not in source
    )


def test_obux057_account_snapshot_is_not_just_trading():
    source = text(PROJECTION)

    for token in [
        '"Access"',
        '"Mode"',
        '"Alerts"',
        '"Private Beta"',
        "recentSessions",
        "feedback",
        "notification",
    ]:
        assert token in source


def test_obux057_no_fake_market_fallbacks():
    source = text(PROJECTION)

    assert (
        "sourceBackedCandidates"
        in source
    )

    assert (
        "sourceBackedPositions"
        in source
    )

    assert (
        "sourceBackedReviews"
        in source
    )

    assert (
        "Math.random"
        not in source
    )


def test_obux057_notification_truth_guarded():
    source = text(PROJECTION)

    assert (
        "Email delivery status unavailable"
        in source
    )

    assert (
        "browserNotificationState"
        in source
    )


def test_obux058_sop_is_versioned_carousel():
    source = text(ARRIVAL)

    for token in [
        "ob-carousel-arrow",
        "ob-carousel-dot",
        "ArrowRight",
        "ArrowLeft",
        "touchstart",
        "sopAcknowledgedVersion",
        "acknowledgeSop",
    ]:
        assert token in source


def test_obux058_sop_teaches_actual_flow():
    source = text(ARRIVAL)

    for token in [
        "Dashboard",
        "Market Map",
        "Symbol Room",
        "Trade Center",
        "Review Center",
    ]:
        assert token in source

    assert (
        "proof pages"
        in source.lower()
    )


def test_obux058_checkin_is_optional():
    source = text(ARRIVAL)

    assert (
        "Skip for now"
        in source
    )

    assert (
        "skipCheckIn"
        in source
    )

    assert (
        "This is optional"
        in source
    )


def test_obux058_checkin_cannot_change_market_truth():
    source = (
        text(ARRIVAL)
        + "\n"
        + text(PROJECTION)
    )

    assert (
        "Market truth stays market truth"
        in source
        or "never changes market truth"
        in source.lower()
    )

    assert (
        "checkInChangesMarketTruth"
        in source
    )

    assert (
        "checkInChangesMarketTruth:\n          false"
        in source
    )


def test_obux058_checkin_retention_is_opt_in():
    source = text(SESSION)

    for token in [
        "rememberForPrivateReview",
        "sessionStorage",
        "checkInForHistory",
        "rememberForPrivateReview",
    ]:
        assert token in source


def test_obux058_one_canonical_session_object():
    source = text(SESSION)

    for token in [
        "sopAcknowledgedVersion",
        "whatsNewAcknowledgedVersion",
        "selectedMode",
        "lastSafeRoute",
        "activeRoom",
        "selectedSymbol",
        "notificationReadiness",
        "feedbackThisSession",
        "reflection",
        "returnReason",
        "closeStatus",
    ]:
        assert token in source


def test_obux058_resume_and_refresh_recovery():
    source = (
        text(ARRIVAL)
        + "\n"
        + text(SESSION)
    )

    assert (
        "Continue where I left off"
        in source
    )

    assert (
        "resumeCandidate"
        in source
    )

    assert (
        "does not imply"
        in source.lower()
    )

    assert (
        "brokerage action"
        in source.lower()
    )


def test_obux058_multi_tab_guard():
    source = (
        text(ARRIVAL)
        + "\n"
        + text(SESSION)
    )

    assert (
        "OB is already open"
        in source
    )

    assert (
        "TAB_LEASE_KEY"
        in source
    )

    assert (
        "claimTab"
        in source
    )


def test_obux058_whats_changed_is_versioned():
    source = (
        text(ARRIVAL)
        + "\n"
        + text(SESSION)
    )

    assert (
        "WHATS_NEW"
        in source
    )

    assert (
        "whatsNewAcknowledgedVersion"
        in source
    )

    assert (
        "acknowledgeWhatsNew"
        in source
    )


def test_obux059_guided_real_product_session():
    source = (
        text(ARRIVAL)
        + "\n"
        + text(DASH_JS)
        + "\n"
        + text(GLOBAL)
    )

    assert (
        "Want me to walk with you the first time?"
        in source
    )

    assert (
        "Guide me"
        in source
    )

    assert (
        "No proof pages"
        in source
    )

    assert (
        "Take me to Market Map"
        in source
    )

    assert (
        "Finish guide"
        in source
    )


def test_obux059_feedback_captures_context():
    source = (
        text(GLOBAL)
        + "\n"
        + text(SESSION)
    )

    for token in [
        "room:",
        "mode:",
        "symbol:",
        "build:",
        "sopVersion:",
        "local_queue",
    ]:
        assert token in source


def test_obux059_feedback_delivery_is_truthful():
    source = text(GLOBAL).lower()

    assert (
        "local ob beta feedback queue"
        in source
        or "local ob beta feedback"
        in source
    )

    assert (
        "did not pretend"
        in source
    )


def test_obux059_tower_return_and_ob_signout():
    source = text(GLOBAL)

    assert (
        "/tower/return/observatory"
        in source
    )

    assert (
        "Back to Tower"
        in source
    )

    assert (
        "Sign out of OB"
        in source
    )


def test_obux059_active_tracking_warning():
    source = text(GLOBAL)

    assert (
        "does\n            <strong>not</strong>\n            close a brokerage position"
        in source
    )

    assert (
        "activeTrackedPositions"
        in source
    )


def test_obux059_idle_privacy_lock():
    source = text(GLOBAL)

    assert (
        "Privacy lock"
        in source
    )

    assert (
        "Re-enter through Tower"
        in source
    )

    assert (
        "IDLE_MS"
        in source
    )


def test_obux059_global_shell_on_all_canonical_rooms():
    for path in CORE_TEMPLATES:
        source = text(path)

        assert (
            "ob_session_state.js"
            in source
        ), path

        assert (
            "ob_nav_shell.js"
            in source
        ), path

        assert (
            "ob_global_session_shell.js"
            in source
        ), path


def test_obux059_live_auto_stays_locked():
    source = (
        text(GLOBAL)
        + "\n"
        + text(PROJECTION)
    )

    assert (
        "Live Auto Locked"
        in source
    )

    assert (
        "automatedModeLocked"
        in source
    )

    assert (
        "automaticExecution"
        in source
    )

    assert (
        "automaticContractSelection"
        in source
    )


def test_obux059_manual_live_boundary_explicit():
    source = text(PROJECTION)

    assert (
        "owner chooses and places the trade externally"
        in source
    )

    assert (
        "brokerExecution"
        in source
    )


def test_obux060_legacy_body_replacement_retired():
    source = text(APP)

    assert (
        "response.set_data("
        "_tower_obux006_010_dashboard_server_html()"
        ")"
        not in source
    )


def test_obux060_old_dashboard_ui_stack_not_loaded():
    source = text(DASH)

    forbidden = [
        "ob_dashboard_simplification_obux.js",
        "ob_account_experience.js",
        "ob_mission_accounts.js",
        "ob_market_data.js",
        "ob_owner_dashboard_contract.js",
    ]

    for token in forbidden:
        assert token not in source


def test_obux060_no_direct_execution_code():
    source = "\n".join(
        text(path)
        for path in [
            SESSION,
            ARRIVAL,
            PROJECTION,
            DASH_JS,
            GLOBAL,
        ]
    )

    forbidden = [
        r"\byfinance\b",
        r"\bplaceOrder\s*\(",
        r"\bsubmitOrder\s*\(",
        r"\bexecuteTrade\s*\(",
        r"\bautoExecute\s*\(",
    ]

    for pattern in forbidden:
        assert not re.search(
            pattern,
            source,
            re.I,
        ), pattern


def test_obux060_dark_modal_and_accessibility():
    source = (
        text(CSS)
        + "\n"
        + text(ARRIVAL)
    )

    for token in [
        "ob-modal-backdrop",
        "backdrop-filter",
        "brightness(.22)",
        "aria-modal",
        "trapFocus",
        "prefers-reduced-motion",
    ]:
        assert token in source


def test_obux060_failure_safe_arrival():
    source = text(ARRIVAL)

    assert (
        "OB arrival failed safely"
        in source
    )

    assert (
        "ob-arrival-fallback"
        in source
    )

    assert (
        "ob-arrival-booting"
        in source
    )
